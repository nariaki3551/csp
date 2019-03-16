#!/usr/bin/env python
# coding: utf-8

import networkx as nx

def BellmanFord(MultiGraph, source, target, weight):
    """MultiGraph: networkx multipul directed graph"""
    distance = dict()
    predecessor = dict()

    # Step 1: initialize graph
    for v in MultiGraph:
        distance[v] = float('inf')  # At the beginning , all vertices have a weight of infinity
        predecessor[v] = None     # And a null predecessor

    distance[source] = 0           # The weight is zero at the source

    # Step 2: relax edges repeatedly
    for _ in range(MultiGraph.number_of_nodes()-1):
        is_update = False
        for tail in MultiGraph:
            for head, edges in MultiGraph[tail].items():
                for key, weights in edges.items():
                    w = weights[weight]
                    if distance[tail] + w < distance[head]:
                        distance[head] = distance[tail] + w
                        predecessor[head] = (tail, (tail, head, key))
                        is_update = True
        if not is_update:
            break

    # Step 3: check for negative-weight cycles
    for tail, head, weights in MultiGraph.edges(data=True):
        w = weights[weight]
        if distance[tail] + w < distance[head]:
            print("Graph contains a negative-weight cycle")

    return distance, predecessor


def shortest_path_bf(MultiGraph, source, target, weight):
    if all(weights[weight] >= 0 for _, _, weights in MultiGraph.edges(data=True)):
        path_nodes = nx.shortest_path(MultiGraph, source=source, target=target, weight=weight)
    else:
        path_nodes = nx.bellman_ford_path(MultiGraph, source, target, weight)
    
    path_edges = []
    for tail, head in zip(path_nodes, path_nodes[1:]):
            min_key = min(MultiGraph[tail][head], key=lambda edge_key: MultiGraph[tail][head][edge_key][weight])
            path_edges.append((tail, head, min_key))
    
    return path_nodes, path_edges