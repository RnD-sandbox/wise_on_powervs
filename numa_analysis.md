# Guidelines for AI assistants to analyze NUMA Allocation data in Tables

This Markdown file provides a detailed explanation of the `numactl -H` command, breaks down the example output, and shows how to transform the data into a Markdown file for AI analysis.

NUMA Allocation refers to the process of assigning memory to specific nodes within a NUMA system. This involves determining which memory blocks will be used by which processors, aiming to optimize memory access times based on the system's architecture.

NUMA Placement involves the strategy of placing processes and their associated memory on the appropriate NUMA nodes. This includes deciding which CPUs and memory regions should be used by a process to minimize memory access latency and maximize performance by keeping frequently accessed memory close to the corresponding processors.
 
## Understanding `numactl -H` Command

### 1. What is `numactl -H`?

The `numactl -H` command is used to display information about the NUMA (Non-Uniform Memory Access) nodes on a system. NUMA is a computer memory design used in multiprocessors where the memory access time depends on the memory location relative to a processor. The `numactl -H` command helps in understanding the NUMA configuration of your system, which is crucial for optimizing application performance by leveraging NUMA's architecture.

### 2. Example Output and Explanation

Here is an example output of the `numactl -H` command:

```console
available: 2 nodes (0-1)
node 0 cpus: 0 1 2 3 4 5 6 7
node 0 size: 32768 MB
node 0 free: 16230 MB
node 1 cpus: 8 9 10 11 12 13 14 15
node 1 size: 32768 MB
node 1 free: 15872 MB
node distances:
node 0 1
0: 10 20
1: 20 10
```

#### Breakdown of the Output:

- **`available: 2 nodes (0-1)`**: This indicates that there are 2 NUMA nodes available on the system, identified as node 0 and node 1.

- **`node 0 cpus: 0 1 2 3 4 5 6 7`**: This lists the CPU cores that are associated with node 0. In this case, node 0 has CPU cores 0 through 7.

- **`node 0 size: 32768 MB`**: This shows the total memory size available on node 0, which is 32,768 MB (32 GB).

- **`node 0 free: 16230 MB`**: This shows the free memory available on node 0, which is 16,230 MB (approximately 16 GB).

- **`node 1 cpus: 8 9 10 11 12 13 14 15`**: This lists the CPU cores that are associated with node 1. In this case, node 1 has CPU cores 8 through 15.

- **`node 1 size: 32768 MB`**: This shows the total memory size available on node 1, which is 32,768 MB (32 GB).

- **`node 1 free: 15872 MB`**: This shows the free memory available on node 1, which is 15,872 MB (approximately 15.5 GB).

- **`node distances:`**: This section provides the latency between nodes. Lower values indicate lower latency (faster access). The distances table is symmetrical:
  - The distance from node 0 to itself is 10.
  - The distance from node 0 to node 1 is 20.
  - The distance from node 1 to itself is 10.
  - The distance from node 1 to node 0 is 20.

## 3. Transforming the Data to Markdown Table Format

For AI analysis, especially when dealing with large outputs, it is often useful to transform the data into a Markdown table format. This allows for a clear and structured representation of the data.

Here is how you can represent the given example output in a Markdown table format:

```markdown
| node_ids | cpus_count | memory_size | memory_free |
|----------|------------|-------------|-------------|
| 0        | 8          | 32768 MB    | 16230 MB    |
| 1        | 8          | 32768 MB    | 15872 MB    |
```
#### Explanation of the Markdown Table Columns:
- `node_ids`: This column represents the NUMA node ID.
- `cpus_count`: This column indicates the number of CPU cores associated with the respective NUMA node.
- `memory_size`: This column shows the total memory size of the respective NUMA node in MB.
- `memory_free`: This column shows the free memory available on the respective NUMA node in MB.

## 4. Evaluating NUMA Allocation

To determine if a NUMA allocation is good or bad, we can use the following three conditions:

1. **MIN(cpus_count) greater than or equal to (MAX(cpus_count) / 2)**
2. **MIN(memory_size) greater than or equal to (MAX(memory_size) / 2)**
3. **No node should be assigned only memory or only CPUs**

A numa allocation is good only when all three conditions are true.

### Examples of NUMA Allocations

#### Good NUMA Allocation:
```markdown
| node_ids | cpus_count | memory_size | memory_free |
|----------|------------|-------------|-------------|
| 0        | 8          | 32768 MB    | 16230 MB    |
| 1        | 8          | 32768 MB    | 15872 MB    |
```
- **Evaluation**:
  - Condition 1 satisfied: MIN(cpus_count) = 8, MAX(cpus_count) = 8, and 8 >= 8 / 2.
  - Condition 2 satisfied: MIN(memory_size) = 32768 MB, MAX(memory_size) = 32768 MB, and 32768 MB >= 32768 / 2.
  - Condition 3 satisfied: Both nodes have CPUs and memory.

#### Bad NUMA Allocation Example 1:
```markdown
| node_ids | cpus_count | memory_size | memory_free |
|----------|------------|-------------|-------------|
| 0        | 2          | 32768 MB    | 16230 MB    |
| 1        | 8          | 32768 MB    | 15872 MB    |
```
- **Evaluation**:
  - Condition 1 violated: MIN(cpus_count) = 2, MAX(cpus_count) = 8, and 2 < (8 / 2). MIN(cpus_count) must be at least 4.
  - Condition 2 satisfied: MIN(memory_size) = 32768 MB, MAX(memory_size) = 32768 MB, and 32768 MB >= 32768 / 2.
  - Condition 3 satisfied: Both nodes have CPUs and memory.

#### Bad NUMA Allocation Example 2:
```markdown
| node_ids | cpus_count | memory_size | memory_free |
|----------|------------|-------------|-------------|
| 0        | 8          | 16384 MB    | 8000 MB     |
| 1        | 8          | 32768 MB    | 15872 MB    |
```
- **Evaluation**:
  - Condition 1 satisfied: MIN(cpus_count) = 8, MAX(cpus_count) = 8, and 8 >= (8 / 2).
  - Condition 2 violated: MIN(memory_size) = 16384 MB, MAX(memory_size) = 32768 MB, and 16384 MB < (32768 / 2). MIN(memory_size) must be at least 16384 MB.
  - Condition 3 satisfied: Both nodes have CPUs and memory.

#### Bad NUMA Allocation Example 3:
```markdown
| node_ids | cpus_count | memory_size | memory_free |
|----------|------------|-------------|-------------|
| 0        | 8          | 0 MB        | 0 MB        |
| 1        | 0          | 32768 MB    | 15872 MB    |
```
- **Evaluation**:
  - Condition 1 violated: MIN(cpus_count) = 0, MAX(cpus_count) = 8, and 0 < 8 / 2. MIN(cpus_count) must be at least 4.
  - Condition 2 violated: MIN(memory_size) = 0 MB, MAX(memory_size) = 32768 MB, and 0 MB < (32768 MB / 2). MIN(memory_size) must be at least 16384 MB.
  - Condition 3 violated: Node 0 has only CPUs, and Node 1 has only memory.

By evaluating the NUMA allocations based on these conditions, we can conclude whether the allocation is good or bad. A good allocation meets all three conditions, while a bad allocation fails one or more of these conditions.

## Guidelines for AI assistant to do evaluation NUMA Allocation

Generative AI Models must evaluate if a NUMA Allocation is good or bad when it is provided with a numactl -H output transformed as a markdown table. The evaluation response must contain two parts:
1. Evaluation statement whether the numa allocation is good or bad
2. Explanation section with following segments 
    1. List of conditions that must be fulfilled by a good numa allocation.
    2. Analysis for each condition whether it is satisfied or not satisfied with data from the table.


### Example 1 of user prompt and expected result

**User Prompt**: Evaluate if the given transformed numactl -H command output is a good numa allocation.
```markdown
| node_ids | cpus_count | memory_size | memory_free |
|----------|------------|-------------|-------------|
| 0        | 8          | 32768 MB    | 16230 MB    |
| 1        | 8          | 32768 MB    | 15872 MB    |
```
**Expected AI Assistant response**:
```
EVALUATION:
This is a good numa allocation

EXPLANATION:
A good numa allocation must satisfy following conditions:
- MIN(cpus_count) greater than or equal to (MAX(cpus_count) / 2)
- MIN(memory_size) greater than or equal to (MAX(memory_size) / 2)
- No node should be assigned only memory or only CPUs
Condition 1 satisfied. MIN(cpus_count) = 8, MAX(cpus_count) = 8, and 8 >= 8 / 2.
Condition 2 satisfied. MIN(memory_size) = 32768 MB, MAX(memory_size) = 32768 MB, and 32768 MB >= 32768 / 2.
Condition 3 satisfied. Both nodes have CPUs and memory.
```

### Example 2 of user prompt and expected result

**User Prompt**: Evaluate if the following transformed numactl -H command output shows a good numa allocation.
```markdown
| node_ids | cpus_count | memory_size | memory_free |
|----------|------------|-------------|-------------|
| 0        | 8          | 0 MB        | 0 MB        |
| 1        | 0          | 32768 MB    | 15872 MB    |
```

**Expected AI Assistant response**:
```
EVALUATION:
This is a bad numa allocation

EXPLANATION:
A good numa allocation must satisfy following conditions:
- MIN(cpus_count) greater than or equal to (MAX(cpus_count) / 2)
- MIN(memory_size) greater than or equal to (MAX(memory_size) / 2)
- No node should be assigned only memory or only CPUs
Condition 1 violated: MIN(cpus_count) = 0, MAX(cpus_count) = 8, and 0 < 8 / 2. MIN(cpus_count) must be at least 4.
Condition 2 violated: MIN(memory_size) = 0 MB, MAX(memory_size) = 32768 MB, and 0 MB < (32768 MB / 2). MIN(memory_size) must be at least 16384 MB.
Condition 3 violated: Node 0 has only CPUs, and Node 1 has only memory.
```