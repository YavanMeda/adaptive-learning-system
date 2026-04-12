import argparse
from pathlib import Path

import config
from db import (
    count_rows,
    create_tables,
    find_nearest_node,
    get_node_by_id,
    insert_edge,
    insert_expansion_log,
    insert_node,
    insert_node_chunk,
    is_ancestor,
    retrieve_top_k_chunks,
    truncate_graph_tables,
    update_node_depth_limited,
    update_node_llm_response,
)
from embeddings import embed_text
from llm import call_llm, call_llm_confirm_identity


def load_prompt_template(path):
    return Path(path).read_text(encoding="utf-8")


def format_chunks_for_prompt(chunks):
    blocks = []
    for chunk in chunks:
        subsection_part = (
            f", Subsection {chunk['subsection_idx']}"
            if chunk["subsection_idx"] is not None
            else ""
        )
        blocks.append(
            "\n".join(
                [
                    f"--- CHUNK {chunk['id']} ---",
                    (
                        f"Position: Chapter {chunk['chapter_idx']}, "
                        f"Section {chunk['section_idx']}{subsection_part}"
                    ),
                    f"Heading: {chunk['heading']}",
                    "Content:",
                    chunk["body"],
                    "---",
                ]
            )
        )
    return "\n\n".join(blocks)


def run_expansion(target_label, target_description):
    target_embedding = embed_text(f"{target_label}: {target_description}")
    target_id = insert_node(
        label=target_label,
        description=target_description,
        embedding=target_embedding,
        depth=0,
        is_target=True,
    )

    frontier = [target_id]
    visited = set()
    total_llm_calls = 0
    prerequisite_template = load_prompt_template("prompts/prerequisite.txt")

    while frontier:
        current_id = frontier.pop()

        if current_id in visited:
            continue

        current = get_node_by_id(current_id)

        if current["depth"] >= config.MAX_DEPTH:
            update_node_depth_limited(current_id)
            visited.add(current_id)
            insert_expansion_log(current_id, "depth_limited", {"depth": current["depth"]})
            print(f"[DFS] Depth limit reached: {current['label']} (depth {current['depth']})")
            continue

        visited.add(current_id)
        print(
            f"[DFS] Expanding: {current['label']} (depth {current['depth']}, "
            f"visited {len(visited)}, frontier {len(frontier)})"
        )

        candidate_chunks = retrieve_top_k_chunks(current["embedding"], k=config.K_CHUNKS)
        if not candidate_chunks:
            insert_expansion_log(current_id, "no_chunks_found", {})
            print(f"[DFS] WARNING: No chunks found for {current['label']}")
            continue

        chunks_formatted = format_chunks_for_prompt(candidate_chunks)
        user_prompt = prerequisite_template.format(
            prerequisite_cap=config.PREREQUISITE_CAP,
            concept_label=current["label"],
            concept_description=current["description"],
            chunks_formatted=chunks_formatted,
        )
        response = call_llm(
            system_prompt=(
                "You are a prerequisite analysis system. "
                "You respond only with valid JSON."
            ),
            user_prompt=user_prompt,
        )
        total_llm_calls += 1
        update_node_llm_response(current_id, response)

        prerequisites = response.get("prerequisites", [])[: config.PREREQUISITE_CAP]
        definitional_chunk_ids = response.get("definitional_chunk_ids", [])

        valid_chunk_ids = {chunk["id"] for chunk in candidate_chunks}
        definitional_chunk_ids = [
            chunk_id for chunk_id in definitional_chunk_ids if chunk_id in valid_chunk_ids
        ]

        for chunk_id in definitional_chunk_ids:
            insert_node_chunk(current_id, chunk_id, "definitional")

        for prereq in prerequisites:
            prereq_label = prereq.get("label", "").strip()
            prereq_description = prereq.get("description", "").strip()
            if not prereq_label or not prereq_description:
                continue

            informing_chunk_ids = [
                chunk_id
                for chunk_id in prereq.get("informing_chunk_ids", [])
                if chunk_id in valid_chunk_ids
            ]

            prereq_embedding = embed_text(f"{prereq_label}: {prereq_description}")
            match, similarity = find_nearest_node(prereq_embedding, exclude_id=None)
            resolved_node_id = None

            if match is not None and similarity >= config.HIGH_THRESHOLD:
                resolved_node_id = match["id"]
                insert_expansion_log(
                    current_id,
                    "dedup_auto_merge",
                    {
                        "candidate_label": prereq_label,
                        "matched_label": match["label"],
                        "similarity": similarity,
                    },
                )
                print(
                    f"  [DEDUP] Auto-merge: '{prereq_label}' -> '{match['label']}' "
                    f"(sim={similarity:.4f})"
                )
            elif match is not None and similarity >= config.BORDERLINE_THRESHOLD:
                is_same = call_llm_confirm_identity(
                    prereq_label,
                    prereq_description,
                    match["label"],
                    match["description"],
                )
                total_llm_calls += 1
                if is_same:
                    resolved_node_id = match["id"]
                    insert_expansion_log(
                        current_id,
                        "dedup_llm_merge",
                        {
                            "candidate_label": prereq_label,
                            "matched_label": match["label"],
                            "similarity": similarity,
                            "llm_decision": "same",
                        },
                    )
                    print(
                        f"  [DEDUP] LLM confirmed merge: '{prereq_label}' -> "
                        f"'{match['label']}' (sim={similarity:.4f})"
                    )
                else:
                    insert_expansion_log(
                        current_id,
                        "dedup_llm_split",
                        {
                            "candidate_label": prereq_label,
                            "matched_label": match["label"],
                            "similarity": similarity,
                            "llm_decision": "different",
                        },
                    )
                    print(
                        f"  [DEDUP] LLM rejected merge: '{prereq_label}' != "
                        f"'{match['label']}' (sim={similarity:.4f})"
                    )

            if resolved_node_id is None:
                new_id = insert_node(
                    label=prereq_label,
                    description=prereq_description,
                    embedding=prereq_embedding,
                    depth=current["depth"] + 1,
                )
                resolved_node_id = new_id
                insert_expansion_log(
                    current_id,
                    "new_node",
                    {
                        "label": prereq_label,
                        "nearest_similarity": similarity if match else None,
                    },
                )
                print(f"  [NEW] Created node: '{prereq_label}' (depth {current['depth'] + 1})")
                if new_id not in visited:
                    frontier.append(new_id)

            if is_ancestor(resolved_node_id, current_id):
                insert_edge(resolved_node_id, current_id, is_back_edge=True)
                insert_expansion_log(
                    current_id,
                    "back_edge",
                    {"from": resolved_node_id, "to": current_id},
                )
                print(
                    f"  [CYCLE] Back edge detected and flagged: "
                    f"node {resolved_node_id} -> node {current_id}"
                )
            else:
                insert_edge(resolved_node_id, current_id, is_back_edge=False)

            for chunk_id in informing_chunk_ids:
                insert_node_chunk(resolved_node_id, chunk_id, "prerequisite-informing")

    print("\n[DFS] Expansion complete.")
    print(f"  Nodes: {len(visited)}")
    print(f"  LLM calls: {total_llm_calls}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true")
    parser.add_argument("target_label")
    parser.add_argument("target_description")
    args = parser.parse_args()

    create_tables()
    if args.reset:
        truncate_graph_tables()
    else:
        existing = count_rows("nodes")
        if existing:
            print(
                f"[ERROR] The nodes table is not empty ({existing} rows found). "
                "Pass --reset to clear prior graph"
            )
            print(
                "        data before running a new expansion, or inspect the existing graph with"
            )
            print("        linearise.py and evaluate.py.")
            raise SystemExit(1)

    run_expansion(args.target_label, args.target_description)


if __name__ == "__main__":
    main()

