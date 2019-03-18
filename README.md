## eppstein

Algorithm for finding the k shortest path problem

* eppstein.ipynb (for DiGraph)
* eppstein_multi.ipynb (for MultiDiGraph)
* heap_tree (for eppstein*.ipynb)



## dual_algorithm

Algorithm for finding constrained shroetst path problem

+ dual_algorithm.py (main code)
+ ShortestPath.py
+ EppsteinKSP.py
+ YenKSP.py
+ heap_tree.py



## Usage

```python
Usage:
    dual_algorithm.py graph_file source target upper_bound [--print_path] [--yen]

Options:
    --print_path
    --yen        : Use Yen algorithm for the k shortest path problem

Notes:
    Build Date: Mar 7 2019
    Main Algorithm            : Hander-Zang algorithm
    Shortest Path Algorithm   : Dijkstr algorithm
                              : Bellman-Ford algorithm
    K Shortest Path Algorithm : Eppstein algorithm
                              : Yen algorithm

Graph (Multipul Directed Graph):
    format of graph_fileis 
    tail_node,head_node,weight(float),cost(float)
```



**sample**

```bash
$ python dual_algorithm.py graph_data/fig1_graph.csv 1 10 1

Build Date: Mar 07 2019
Main Algorithm            : Hander-Zang algorithm
Shortest Path Algorithm   : Dijkstra or Bellman-Ford algorithm
K Shortest Path Algorithm : Eppstein algorithm

the number of nodes: 10
the number of edges: 22

Remove the nodes which does not contained source - target path (#STEP0)
remained the number of nodes: 10
remained number of edges: 22

We obtain shortest path on weight (#STEP1)
    f = 5.000, g = 2.000

We obtain shortest path on cost (#STEP2)
    f = 20.000, g = 0.350

Best Solution:  20.000

------------------------------------------------------------
 Iter Step Update    Best      LB      UB     Gap    Time
------------------------------------------------------------
    1   #1     LB       -    5.00       -      -%      0s
    2   #2     UB   20.00    5.00   20.00  78.95%      0s
    3   #3          20.00    5.00   20.00  78.95%      0s
    4   #3     UB   15.00    5.00   15.00  71.43%      0s
    5   #3     LB   15.00   11.00   15.00  28.57%      0s
    6   #4     LB   15.00   12.00   15.00  21.43%      0s
    7   #4  LB UB   14.00   13.00   14.00   7.69%      0s
    8   #4     LB   14.00   13.50   14.00   3.85%      0s
    9   #4     LB   14.00   15.00   14.00  -7.69%      0s



*Optimal Solution: 14.00
    path [('1', '3', 0), ('3', '6', 0), ('6', '10', 0)]
    f = 14.000, g = 0.900
```

