To identify bottlenecks, perform the following steps:
1. Identify the nodes with the least and most number of cpus.
2. Identify the nodes with the least and most amount of memory.
3. Check whether the values fulfill the following four criteria:
    1. min cpu >= (max cpu / 2)
    2. min memory >= (max memory / 2)
    3. min cpu > 0. Every node has at least one cpu assigned to it.
    4. min memory > 0. Every node has at least 1MB of RAM assigned to it.