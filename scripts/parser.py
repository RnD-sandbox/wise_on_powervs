import os
import re

base_instruction = """You are AI assistant to support the Non-uniform memory access(NUMA) allocation analysis. To ensure good performance of NUMA placement should satisfy the following 3 conditions.
1. min(CPUs) >= (max(CPUs) / 2 )
2. min(Memory Size) >= (max(Memory Size) / 2) 
3. No node should be assigned only memory or only cpus
When a numactl command execution result is provided, you must analyse, reason and deduct if the above conditions are met."""


def parse_numactl(file_path):
    with open(file_path, "r") as file:
        data = file.read()

    # Extract total nodes string
    total_nodes_info = re.search(r"available:\s*(.+)", data)
    total_nodes_info_str = (
        total_nodes_info.group(1) if total_nodes_info else "Not found"
    )

    # Extract total number of nodes
    nodes = re.findall(r"available: \d+ nodes \(([\d,-]+)\)", data)
    if nodes:
        total_nodes = len(nodes[0].split(","))
    else:
        total_nodes = 0

    # Extract CPUs assigned to each node, including nodes with no CPUs
    cpus_per_node = {}
    cpu_info = re.findall(r"node (\d+) cpus: ([\d ]*)", data)
    all_nodes = re.findall(r"node (\d+)", data)

    for node in all_nodes:
        if int(node) not in cpus_per_node:
            cpus_per_node[int(node)] = 0  # default value
    for node, cpus in cpu_info:
        cpus_per_node[int(node)] = len(cpus.split()) if cpus.strip() else 0

    # Extract memory info
    memory_info = {}
    memory_size = re.findall(r"node (\d+) size: (\d+) MB", data)
    memory_free = re.findall(r"node (\d+) free: (\d+) MB", data)
    for node, size in memory_size:
        memory_info[int(node)] = {"size": int(size), "free": 0}
    for node, free in memory_free:
        memory_info[int(node)]["free"] = int(free)

    # Extract latency info
    latency_info = []
    latency_lines = re.findall(r"node distances:\n([\s\d:]+)", data, re.DOTALL)
    if latency_lines:
        latency_info = [line.split() for line in latency_lines[0].split("\n") if line]

    return {
        "total_nodes_info": total_nodes_info_str,
        "total_nodes": total_nodes,
        "cpus_per_node": cpus_per_node,
        "memory_info": memory_info,
        "latency_info": latency_info,
    }


def process_folder(folder_path):
    results = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".txt"):
            file_path = os.path.join(folder_path, file_name)
            result = parse_numactl(file_path)
            results.append((file_name, result))
    return results


def print_results(results):
    for file_name, result in results:
        print(f"Results for {file_name}:")
        print(f"  Total nodes info: {result['total_nodes_info']}")
        print(f"  Total nodes: {result['total_nodes']}")
        print(f"  Node information:")
        for node, cpus in result["cpus_per_node"].items():
            mem_info = result["memory_info"].get(node, {"size": "N/A", "free": "N/A"})
            print(
                f"    Node {node}: cpus = {cpus}, mem_size = {mem_info['size']} MB, mem_free = {mem_info['free']} MB"
            )
        print(f"  Latency info:")
        for line in result["latency_info"]:
            print("    ", " ".join(line))
        print()


def generate_markdown_table(result):
    markdown_table = "| Node | CPUs | Memory Size (MB) | Memory Free (MB) |\n"
    markdown_table += "|------|------|-----------------|-----------------|\n"

    for node, cpus in result["cpus_per_node"].items():
        mem_info = result["memory_info"].get(node, {"size": "N/A", "free": "N/A"})
        markdown_table += (
            f"| {node} | {cpus} | {mem_info['size']} | {mem_info['free']} |\n"
        )

    return markdown_table


def check_numa_conditions(result):
    cpus_per_node = result["cpus_per_node"]
    memory_info = result["memory_info"]

    cpu_counts = list(cpus_per_node.values())
    mem_sizes = [info["size"] for info in memory_info.values()]

    min_cpus = min(cpu_counts)
    max_cpus = max(cpu_counts)
    min_mem_size = min(mem_sizes)
    max_mem_size = max(mem_sizes)

    condition1 = min_cpus >= (max_cpus / 2)
    condition2 = min_mem_size >= (max_mem_size / 2)
    condition3 = all(
        cpus > 0 and memory_info[node]["size"] > 0
        for node, cpus in cpus_per_node.items()
    )

    return (
        condition1,
        condition2,
        condition3,
        min_cpus,
        max_cpus,
        min_mem_size,
        max_mem_size,
    )


def classify_numa_allocation(result):
    (
        condition1,
        condition2,
        condition3,
        min_cpus,
        max_cpus,
        min_mem_size,
        max_mem_size,
    ) = check_numa_conditions(result)
    explanations = []

    if not condition1:
        violating_nodes = [
            node for node, cpus in result["cpus_per_node"].items() if cpus == min_cpus
        ]
        explanations.append(
            f"Condition 1 violated: Minimum CPUs in any node ({min_cpus}) is less than half of the maximum CPUs in any node ({max_cpus}). Violating nodes: {violating_nodes}."
        )
    if not condition2:
        violating_nodes = [
            node
            for node, info in result["memory_info"].items()
            if info["size"] == min_mem_size
        ]
        explanations.append(
            f"Condition 2 violated: Minimum memory size in any node ({min_mem_size} MB) is less than half of the maximum memory size in any node ({max_mem_size} MB). Violating nodes: {violating_nodes}."
        )
    if not condition3:
        violating_nodes = [
            node
            for node, cpus in result["cpus_per_node"].items()
            if cpus == 0 or result["memory_info"].get(node, {"size": 0})["size"] == 0
        ]
        explanations.append(
            f"Condition 3 violated: At least one node is assigned only memory or only CPUs. Violating nodes: {violating_nodes}."
        )

    if all([condition1, condition2, condition3]):
        classification = "Good NUMA allocation"
        explanations.append(
            "All conditions are met, ensuring balanced NUMA allocation."
        )
    else:
        classification = "Bad NUMA allocation"

    return classification, explanations


# Folder path where the text files are stored
folder_path = "numa_logs/test"

# Process the folder and print the results
results = process_folder(folder_path)

# Generate and print markdown tables for each file, classify and explain the NUMA allocation
for file_name, result in results:
    print(f"Markdown table for {file_name}:")
    markdown_table = generate_markdown_table(result)
    print(markdown_table)

    classification, explanations = classify_numa_allocation(result)
    print(f"Classification: {classification}")
    print(f"Explanation:")
    for explanation in explanations:
        print(f"{explanation}")
    print()
