#!/usr/bin/env python
# coding: utf-8

import networkx as nx
from copy import deepcopy
from heapq import heappush, heappop

from ShortestPath import shortest_path_bf
from heap_tree import BinaryTree

def EppsteinKSP(MultiGraph, source, target, weight):
    """ generator k shortest path """
    pred, distance = nx.dijkstra_predecessor_and_distance(MultiGraph.reverse(), source=target, weight=weight)
    # shortest path tree
    T = nx.MultiDiGraph()
    for tail, heads in pred.items():
        if heads:
            head = heads[0]
            min_key = min(MultiGraph[tail][head], key=lambda edge_key: MultiGraph[tail][head][edge_key][weight])
            edge_weight = MultiGraph[tail][head][min_key][weight]
            T.add_edge(tail, head, weight=edge_weight, key=min_key)

    # calc potential of edge
    for tail in MultiGraph:
        for head, edges in MultiGraph[tail].items():
            for key in edges:
                edges[key]['delta'] = edges[key][weight] + distance[head] - distance[tail]

    # generate H_out tree
    def out(tail):
        out_edges = []
        for head, edges in MultiGraph[v].items():
            for key in edges:
                if head not in T[tail] or key not in T[tail][head]:
                    out_edges.append((tail, head, key))
        return out_edges

    for v in MultiGraph:
        out_edges = sorted(out(v))
        h_out_tree = BinaryTree()
        if out_edges:
            max_root, *other_edges = out_edges
            for edge in other_edges:
                h_out_tree.insert(edge, MultiGraph.edges[edge]['delta'])
            h_out_tree.insert(max_root, MultiGraph.edges[max_root]['delta'])
        MultiGraph.node[v]['H_out'] = h_out_tree

    # generate H_T tree
    h_t_tree = BinaryTree()
    out_root = MultiGraph.node[target]['H_out'].root
    if out_root is not None:
        h_t_tree.insert(out_root.name, out_root.value)
    MultiGraph.node[target]['H_T'] = h_t_tree
    for edge in nx.bfs_edges(T.reverse(), source=target):
        tail, head = edge
        h_t_tree = deepcopy(MultiGraph.node[tail]['H_T'])
        out_root = MultiGraph.node[head]['H_out'].root
        if out_root is not None:
            h_t_tree.insert(out_root.name, out_root.value)
        MultiGraph.node[head]['H_T'] = h_t_tree

    # generate H_G tree
    h_g_tree = deepcopy(MultiGraph.node[target]['H_T'])
    h_g_tree.h_out_insert(MultiGraph.node[target]['H_out'])
    MultiGraph.node[target]['H_G'] = h_g_tree
    for edge in nx.bfs_edges(T.reverse(), source=target):
        _, child = edge
        h_g_tree = MultiGraph.node[child]['H_T']
        for v in nx.shortest_path(T, source=child, target=target):
            h_g_tree.h_out_insert(MultiGraph.node[v]['H_out'])
        MultiGraph.node[child]['H_G'] = h_g_tree

    # generate path-graph P
    def edge2delta(edge):
        tail, head, key = edge
        return MultiGraph[tail][head][key]['delta']

    def add_H_G_to_P(node):
        for v in MultiGraph.node[node]['H_G'].traverse():
            v_name = (node, v.name)
            P.add_node(v_name)
            if v.left  is not None:
                u_name = (node, v.left.name)
                edge_weight = edge2delta(v.left.name) - edge2delta(v.name)
                P.add_edge(v_name, u_name, weight=edge_weight, edge_type='heap_edge')
            if v.right is not None:
                u_name = (node, v.right.name)
                edge_weight = edge2delta(v.right.name) - edge2delta(v.name)
                P.add_edge(v_name, u_name, weight=edge_weight, edge_type='heap_edge')
            if v.h_out is not None:
                u_name = (node, v.h_out.name)
                edge_weight = edge2delta(v.h_out.name) - edge2delta(v.name)
                P.add_edge(v_name, u_name, weight=edge_weight, edge_type='heap_edge')

    ## add heap edges
    P = nx.DiGraph()    
    add_H_G_to_P(target)
    for edge in nx.bfs_edges(T.reverse(), source=target):
        _, child = edge
        add_H_G_to_P(child)

    ## add cross edges
    for v in P:
        _, edge = v
        tail, head, key = edge
        if head not in T[tail] or key not in T[tail][head]:
            _, w, key = edge
            if MultiGraph.node[w]['H_G'].root is not None:
                u_name = (w, MultiGraph.node[w]['H_G'].root.name)
                edge_weight = edge2delta(MultiGraph.node[w]['H_G'].root.name)
                P.add_edge(v, u_name, weight=edge_weight, edge_type='cross_edge')

    ## add root node
    P.add_node('RootNode')
    u = (source, MultiGraph.node[source]['H_G'].root.name)
    edge_weight = edge2delta(MultiGraph.node[source]['H_G'].root.name)
    P.add_edge('RootNode', u, weight=edge_weight, edge_type='root_edge')
    
    # find K - shortest path
    def sidetracks2path(sidetracks, source, target, minus_weight):
        tmp_T = T.copy()
        for v, u in sidetracks[1:]:
            if P[v][u]['edge_type'] == 'cross_edge':
                tail, head, key = v[1]
                tmp_T.add_edge(tail, head, key=key, weight=minus_weight)
        if len(sidetracks) > 1:
            _, last_sidetracks = sidetracks[-1]
            tail, head, key = last_sidetracks[1]
            tmp_T.add_edge(tail, head, key=key, weight=minus_weight)
        _, shortest_path_edges = shortest_path_bf(tmp_T, source, target, weight='weight')
        return shortest_path_edges

    minus_weight = -sum(abs(edge_data['weight']) for tail, head in T.edges() for edge_data in T[tail][head].values())
    B = [(0, [(None, 'RootNode')])]
    while B:
        potentials, sidetracks = heappop(B)
        path_edges = sidetracks2path(sidetracks, source, target, minus_weight) 
        yield None, path_edges
        _, last_sidetracks = sidetracks[-1]
        for v in P[last_sidetracks]:
            new_sidetracks = sidetracks + [(last_sidetracks, v)]
            new_potentials = potentials + P.edges[last_sidetracks, v]['weight']
            heappush(B, (new_potentials, new_sidetracks))
