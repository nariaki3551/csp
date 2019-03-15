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
    for i in range(MultiGraph.number_of_nodes()-1):
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
    distance, predecessor = BellmanFord(MultiGraph, source, target, weight)

    curr_node = target
    path_nodes = [curr_node]
    path_edges = []
    while curr_node != source:
        curr_node, curr_edge = predecessor[curr_node]
        path_nodes.append(curr_node)
        path_edges.append(curr_edge)
    path_nodes = path_nodes[::-1]
    path_edges = path_edges[::-1]

    return path_nodes, path_edges