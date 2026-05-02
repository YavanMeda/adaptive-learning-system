import json
import os
import re
import shutil
from collections import Counter
from datetime import datetime

from graphviz import Digraph

import config
from db import (
    create_tables,
    get_all_edges,
    get_all_expansion_logs,
    get_all_nodes,
    get_node_chunks,
)


def slugify(value):
    text = value.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_") or "unknown"


def build_run_metadata():
    nodes = get_all_nodes()
    target_concept = next((node["label"] for node in nodes if node["is_target"]), "unknown")
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    target_slug = slugify(target_concept)
    suffix = (
        f"__{run_id}__{config.CORPUS_ID}__{target_slug}"
        f"__d{config.MAX_DEPTH}_k{config.K_CHUNKS}_cap{config.PREREQUISITE_CAP}"
    )
    return {
        "run_id": run_id,
        "target_concept": target_concept,
        "suffix": suffix,
    }


def generate_dag_visualisation(run_meta):
    nodes = get_all_nodes()
    edges = get_all_edges()

    os.makedirs("output", exist_ok=True)
    dot = Digraph(comment="Prerequisite DAG", format="png")
    dot.attr(rankdir="BT")
    dot.attr("node", shape="box", style="rounded", fontsize="10", fontname="Helvetica")

    for node in nodes:
        label = node["label"]
        if node["is_target"]:
            dot.node(str(node["id"]), label, style="rounded,bold", color="red")
        elif node["is_depth_limited"]:
            dot.node(str(node["id"]), label, style="rounded,dashed", color="gray")
        else:
            dot.node(str(node["id"]), label)

    for edge in edges:
        if edge["is_back_edge"]:
            dot.edge(
                str(edge["source_id"]),
                str(edge["target_id"]),
                style="dashed",
                color="red",
                label="back",
            )
        else:
            dot.edge(str(edge["source_id"]), str(edge["target_id"]))

    output_base = f"output/dag{run_meta['suffix']}"
    dot.render(output_base, cleanup=True)
    print(f"[EVAL] DAG visualisation saved to {output_base}.png")
    if config.WRITE_LATEST_COMPAT_OUTPUTS:
        latest_path = "output/dag.png"
        shutil.copyfile(f"{output_base}.png", latest_path)
        print(f"[EVAL] Latest compatibility copy saved to {latest_path}")


def print_summary_statistics():
    nodes = get_all_nodes()
    edges = get_all_edges()
    non_back_edges = [edge for edge in edges if not edge["is_back_edge"]]
    back_edges = [edge for edge in edges if edge["is_back_edge"]]

    if not nodes:
        print("\n=== EVALUATION SUMMARY ===")
        print("No nodes found. Run expand.py before evaluate.py.")
        return

    depths = [node["depth"] for node in nodes]
    prereq_counts = {}
    for edge in non_back_edges:
        prereq_counts[edge["target_id"]] = prereq_counts.get(edge["target_id"], 0) + 1

    nodes_without_chunks = sum(1 for node in nodes if len(get_node_chunks(node["id"])) == 0)

    print("\n=== EVALUATION SUMMARY ===")
    print(f"Total nodes:              {len(nodes)}")
    print(f"Total edges:              {len(non_back_edges)}")
    print(f"Back edges (cycles):      {len(back_edges)}")
    print(f"Depth range:              {min(depths)} — {max(depths)}")
    print(f"Depth distribution:       {dict(sorted(Counter(depths).items()))}")
    print(f"Max fan-out:              {max(prereq_counts.values()) if prereq_counts else 0}")
    if prereq_counts:
        print(f"Avg fan-out:              {sum(prereq_counts.values()) / len(prereq_counts):.1f}")
    print(f"Nodes without chunks:     {nodes_without_chunks}")
    print(f"Depth-limited nodes:      {sum(1 for node in nodes if node['is_depth_limited'])}")


def export_eval_record(run_meta):
    nodes = get_all_nodes()
    edges = get_all_edges()
    non_back_edges = [edge for edge in edges if not edge["is_back_edge"]]
    depths = [node["depth"] for node in nodes]

    record = {
        "run_id": run_meta["run_id"],
        "timestamp": datetime.now().isoformat(),
        "corpus": config.CORPUS_ID,
        "target_concept": run_meta["target_concept"],
        "config": {
            "MAX_DEPTH": config.MAX_DEPTH,
            "K_CHUNKS": config.K_CHUNKS,
            "HIGH_THRESHOLD": config.HIGH_THRESHOLD,
            "BORDERLINE_THRESHOLD": config.BORDERLINE_THRESHOLD,
            "PREREQUISITE_CAP": config.PREREQUISITE_CAP,
            "LLM_MODEL": config.LLM_MODEL,
            "EMBEDDING_MODEL": config.EMBEDDING_MODEL,
            "MAX_CHUNK_TOKENS": config.MAX_CHUNK_TOKENS,
        },
        "node_count": len(nodes),
        "edge_count": len(non_back_edges),
        "back_edge_count": len(edges) - len(non_back_edges),
        "max_depth_reached": max(depths) if depths else None,
        "depth_distribution": dict(sorted(Counter(depths).items())) if depths else {},
        "depth_limited_nodes": sum(1 for node in nodes if node["is_depth_limited"]),
        "precision_level_1": None,
        "recall_level_1": None,
        "precision_level_2": None,
        "recall_level_2": None,
        "spurious_node_count": None,
        "false_merge_count": None,
        "false_split_count": None,
        "chunk_link_accuracy": None,
        "sequence_coherence": None,
        "notes": "",
    }

    os.makedirs("output", exist_ok=True)
    output_path = f"output/eval_record{run_meta['suffix']}.json"
    with open(output_path, "w", encoding="utf-8") as file_obj:
        json.dump(record, file_obj, indent=2)

    print(f"[EVAL] Evaluation record saved to {output_path}")
    if config.WRITE_LATEST_COMPAT_OUTPUTS:
        latest_path = "output/eval_record.json"
        with open(latest_path, "w", encoding="utf-8") as file_obj:
            json.dump(record, file_obj, indent=2)
        print(f"[EVAL] Latest compatibility copy saved to {latest_path}")
    print("       Fill in manual evaluation fields after inspection.")


def dump_expansion_log(run_meta):
    logs = get_all_expansion_logs()
    os.makedirs("output", exist_ok=True)

    output_path = f"output/expansion_log{run_meta['suffix']}.json"
    with open(output_path, "w", encoding="utf-8") as file_obj:
        json.dump(logs, file_obj, indent=2, default=str)
    if config.WRITE_LATEST_COMPAT_OUTPUTS:
        latest_path = "output/expansion_log.json"
        with open(latest_path, "w", encoding="utf-8") as file_obj:
            json.dump(logs, file_obj, indent=2, default=str)
        print(f"[EVAL] Latest compatibility copy saved to {latest_path}")

    print("\n=== EXPANSION LOG ===")
    if not logs:
        print("No expansion log entries found.")
    else:
        for log in logs:
            print(
                f"{log['created_at']} | node={log['node_id']} | "
                f"{log['event_type']} | {json.dumps(log['detail'])}"
            )
    print(f"[EVAL] Expansion log saved to {output_path}")


def main():
    create_tables()
    run_meta = build_run_metadata()
    generate_dag_visualisation(run_meta)
    print_summary_statistics()
    export_eval_record(run_meta)
    dump_expansion_log(run_meta)


if __name__ == "__main__":
    main()
