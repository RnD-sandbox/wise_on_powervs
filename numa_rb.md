# NUMA

NUMA is used in IBM Power Architecture® platforms. In a system that has NUMA characteristics, each processor has local memory that is available, but it can access memory that is assigned to other processors. The memory access time is faster for local memory. A NUMA node is a collection of processors and memory that is mutually close. Memory access times within a node are faster than outside of a node.

Power Architecture maps memory by locality (core, chip, dual chip module/ socket, node, and others). The memory affinity process locality can impact performance on any system.

With IBM POWER9 processors, the interconnect bandwidth on each node and across multiple nodes is improved by 4x compared to IBM POWER8 processors. This situation results in the improvement of throughput and reduction of latency for SAP applications running on IBM POWER9 processor-based systems compared to their IBM POWER8 predecessors.

## Viewing the NUMA topology from inside the operating system
Looking at the NUMA topology from inside a Linux operating system requires knowledge about what information is updated because the LPAR placement can change after a Live Partition Mobility (LPM) operation or similar tasks. The command that is used is updated only after a restart, so it might display outdated information. For the current information, you must do a memory dump on the HMC, as described in “Viewing the LPAR placement from the HMC” on page 23.

Log in to the LPAR and ensure that the numactl --hardware command has a symmetric output. Confirm that every NUMA node with a core holds memory too. Nodes without cores might not hold memory too, which is often the case for NUMA node 0 not having cores or memory assigned. In such a case, SAP HANA internally maps all NUMA nodes and works only with nodes with both CPU and memory. Therefore, it has no impact on HANA.

## Background on empty NUMA node0
NUMA node 0 historically comes from a bare metal installation where it was part of a sequence of NUMA nodes starting with 0. Later in first virtualized environments, this designation was kept as a constant to represent an anchor point. Today, an empty NUMA node 0 is a legacy item. In current implementations, troubleshooting an empty node0 is irrelevant because it has no functions and no impact because HANA is fully aware of this concept.

The examples 1 and 2 below show that NUMA node 0 has no cores or memory that is associated with it. SAP HANA detected it and listed a number of NUMA nodes with logical CPU, allowed memory, and both CPUs and Memory as 1, ignoring NUMA node 0.

### Example 2

**Command:**
```bash
hd1adm@LINUXLPAR:/usr/sap/HD1/HDB00> numactl --hardware
```
**Output:**
```
available: 2 nodes (0,6)
node 0 cpus:
node 0 size: 0 MB
node 0 free: 0 MB
node 6 cpus: 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 node 6 size: 245201 MB
node 6 size: 245201 MB
node 6 free: 125343 MB
node distances:
node  0  6
  0: 10 40
  6: 40 10
```

### Example 2

**Command:**
```bash
hd1adm@LINUXLPAR:/usr/sap/HD1/HDB00> hdbcons "mm numa -t"
```
**Output:**
```
## Start command at: 2020-03-20 11:57:37.796 *************************************************************
Configuration of NUMA topology *************************************************************
Is NUMA-awareness enabled? (0|1) :  1
      Valid NUMA Topology? (0|1) :  1
            Number of NUMA Nodes :  2
Number of NUMA Nodes with logical cpus :    1
Number of NUMA Nodes with allowed memory:    1
Number of NUMA Nodes with both cpus and memory:    1
              Number of Logical cpus  :   16
                    Cpu-only node IDs : NONE
                    Mem-only node IDs : NONE
*************************************************************
[OK]
## Finish command at: 2020-03-20 11:57:37.796 command took: 112.000 usec
```

Similarly, you can also check other hdbcons options such as "jexec info", which lists an active NUMA node as 1. In this case, as shown in Example 3, the command ignores a NUMA node with no memory and no CPU.

### Example 3

**Command:**
```bash
hd1adm@LINUXLPAR:/usr/sap/HD1/HDB00> hdbcons "jexec info"
```
**Output:**

```
## Start command at: 2020-03-20 11:58:34.289
Using 2 numa nodes
SMT level: 8 using 2 physical cores
numa_features: 1, config: -1
bind_workers: 1, config: -1
max_concurrency: 16 (cfg=, dyn=17)
max_concurrency_hint: 17 (cfg=0)
min_concurrency_hint: 4 (cfg=0)
concurrency_policy: 2 (cfg=0)
max_concurrency_min_pct: 30
max_concurrency_hint_min_pct: 50
stealing_policy: 11 (cfg=0)
0 statement limiters
System info:
2 possible NUMA nodes, 40 possible cores, 1 active NUMA nodes, 16 active logical cores
Using global restriction to a subset of cores: [11111111 11111111 00000000
00000000 00000000 ]
Numa node [0], Socket ID [0]: usable cores=0, available memory=0 KB
  has 1 neighbors: 1
  max_concurrency: 1, dyn=1
Numa node [1], Socket ID [6]: usable cores=16, available memory=251086144 KB
  has 1 neighbors: 0
    max_concurrency: 16, dyn=16
current memory usage, operative: 14560, background: 652912
[OK]
## Finish command at: 2020-03-20 11:58:34.289 command took: 17.000 usec
```

Example 4 shows that the LPAR has an uneven NUMA layout. NUMA node 0 has cores but no memory. NUMA node 6 holds all the memory but no cores, which degrades the performance of SAP HANA (more on POWER8 than POWER9 processors).

In this type of setup, when you run your HANA workload, the processor and memory are not on the same NUMA node, which leads to more memory fetches and higher latency. This situation can happen when your Power Systems server is already running multiple LPARs, and newly created LPARs can access only the remaining resources. The hypervisor tries to allocate resources, but fails to provide an ideal setup due to resource constraints. It is always a best practice to get the best allocation, but in a few cases it is not possible.

For better performance, place the memory and processor cores on the same NUMA node. In multi-cores setup, you have multiple NUMA nodes with some memory and some cores, where:
- Access to memory that is in the same node (local memory) is direct with low latency.
- Access to memory that is in another node is achieved through the interlink bus with a
higher latency.

**Command** Image to text
```bash
hd1adm@LINUXLPAR:/usr/sap/HD1/HDB00> numactl --hardware
```

**Output:**
```
available: 2 nodes (0,6)
node 0 cpus: 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63
node 0 size: 0 MB
node 0 free: 0 MB
node 6 cpus: 
node 6 size: 32768 MB
node 6 free: 31649 MB
node distances:
node  0  6
  0: 10 40
  6: 40 10
```

## Viewing the LPAR placement from the HMC

This option always delivers the current information. To create a resource dump, complete the following steps:
1. Open an SSH to the HMC console and go to the command-line login.
2. On the HMC, check which resource dumps are already in the dump directory by running the following command:
```console
hscroot@:~> lsdump -h 
dump_type=resource,name=RSCDUMP.109130D.09000001.20140624 065824,size=2490992,source_size=0 dump_type=resource,name=RSCDUMP.109130D.0B000001.20141114 162422,size=16128,source_size=0
```
3. Run the following startdump command:
startdump -m -t resource -r 'hvlpconfigdata -affinity -domain'
Note: Creating the dump can take a few seconds.
4. Check whether the dump was created by running the ls –ltr /dump or lsdump command: <br>
```console
hscroot@:~> lsdump -h dump_type=resource,name=RSCDUMP.,size=12784,source_size=0 dump_type=resource,name=RSCDUMP.,source_size=0 dump_type=resource,name=RSCDUMP.,source_size=0
```
This dump contains binary and human readable data.
5. Identify the dump by running the following command: <br>
   cat /dump/RSCDUMP.<my dump ID> | more <br>
This command displays a set of data. In the table that is shown, verify that none of the LPAR IDs belonging to a HANA LPAR are spanning the drawers, or download the table to another machine by using the following command: <br>
   scp hscroot@:/dump/RSCDUMP.<my dump ID>.
6. Afteryoudownloadandcheckthedumpfile,deleteitontheHMCbyrunningthefollowing command:
hscroot@:~> rmdump -f RSCDUMP.<my Dump ID>

### Analyzing and optimizing NUMA placement
In the newer versions of the firmware, the hypervisor team provided methods to analyze and fix memory placement issues on the SSH shell of the HMC. This process is not apparent to the applications and can be run while every LPAR is running if there is available memory on the machine and this feature is enabled. To list the servers, run the following command: <br>
lssyscfg -r sys -F name

**Command** Image to text
```bash
lsmemopt -m power_server_name -r lpar -o currscore
```

**Output:**
```
lpar_name=power_server_name,lpar_id=1,curr_lpar_score=100
lpar_name=power_server_name,lpar_id=2,curr_lpar_score=100
lpar_name=power_server_name,lpar_id=3,curr_lpar_score=none
lpar_name=power_server_name,lpar_id=4,curr_lpar_score=100
lpar_name=power_server_name,lpar_id=5,curr_lpar_score=none
lpar_name=power_server_name,lpar_id=6,curr_lpar_score=100
lpar_name=power_server_name,lpar_id=8,curr_lpar_score=74
lpar_name=power_server_name,lpar_id=12,curr_lpar_score=32
lpar_name=power_server_name,lpar_id=31,curr_lpar_score=none
```

The command does not show the exact placement of memory and cores. Instead, it does a rating, where 100 is the best and 0 is the worst. It rated LPAR 6 with a 100, which means the placement cannot be improved according to the rules of the hypervisor. This example shows that lpar_id 8 does not have a perfect rating.

Running the command as shown in Figure 1-13 with the option -o calcscore shows to what degree the Dynamic Platform Optimizer (DPO) can optimize the LPAR based on the current situation.

To use DPO to optimize the LPARs, run the following command: <br>
optmem -m <Power Server Name> -o start -t affinity -p <name(s) of improvable LPAR(s) >

All other LPARs are candidates to be changed to achieve the best placement. If an LPAR is not touched, another option can be specified (see the man pages for optmem).

Although the command is running in the background, you can check the optimization status by running the following command: <br>
lsmemopt -m <Power Server Name>