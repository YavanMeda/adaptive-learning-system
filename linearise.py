import heapq

from db import create_tables, get_all_edges, get_all_nodes, get_node_by_id, get_node_chunks


def linearise():
    nodes = get_all_nodes()
    edges = [edge for edge in get_all_edges() if not edge["is_back_edge"]]

    in_degree = {node["id"]: 0 for node in nodes}
    dependents = {node["id"]: [] for node in nodes}

    for edge in edges:
        in_degree[edge["target_id"]] += 1
        dependents[edge["source_id"]].append(edge["target_id"])

    node_sort_key = {}
    for node in nodes:
        chunks = get_node_chunks(node["id"])
        if chunks:
            node_sort_key[node["id"]] = min(
                chunk["chapter_idx"] * 1000 + chunk["section_idx"] for chunk in chunks
            )
        else:
            node_sort_key[node["id"]] = 999999

    queue = []
    for node in nodes:
        if in_degree[node["id"]] == 0:
            heapq.heappush(queue, (node_sort_key[node["id"]], node["id"]))

    sequence = []
    while queue:
        _, node_id = heapq.heappop(queue)
        sequence.append(node_id)
        for dep_id in dependents[node_id]:
            in_degree[dep_id] -= 1
            if in_degree[dep_id] == 0:
                heapq.heappush(queue, (node_sort_key[dep_id], dep_id))

    if len(sequence) != len(nodes):
        orphaned = set(node["id"] for node in nodes) - set(sequence)
        print(f"[WARN] Topological sort incomplete. {len(orphaned)} nodes not reached.")
        print(f"  Orphaned node IDs: {orphaned}")
        for node_id in sorted(orphaned, key=lambda item: node_sort_key[item]):
            sequence.append(node_id)

    print(f"\n{'Pos':<5} {'Label':<40} {'Depth':<6} {'Chunks':<7} {'Prereqs':<8} {'Dependents':<10}")
    print("-" * 116)
    for pos, node_id in enumerate(sequence, 1):
        node = get_node_by_id(node_id)
        chunks = get_node_chunks(node_id)
        prereq_count = sum(1 for edge in edges if edge["target_id"] == node_id)
        dep_count = sum(1 for edge in edges if edge["source_id"] == node_id)
        print(
            f"{pos:<5} {node['label']:<40} {node['depth']:<6} "
            f"{len(chunks):<7} {prereq_count:<8} {dep_count:<10}"
        )
    return sequence


def main():
    create_tables()
    linearise()


if __name__ == "__main__":
    main()

