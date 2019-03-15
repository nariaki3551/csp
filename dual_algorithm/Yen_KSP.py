#!/usr/bin/env python
# coding: utf-8

import networkx as nx

from Bellman_Ford import shortest_path_bf

def YenKSP(MultiGraph, source, target, weight):
    """ generator k shortest path """
    #  Determine the shortest path from the source to the sink.
    path_nodes, path_edges = shortest_path_bf(MultiGraph, source, target, weight)
    yield path_nodes, path_edges
    A = [{'node': path_nodes, 'edge': path_edges}]
    # Initialize the set to store the potential kth shortest path.
    B = list()

    k = 0
    while True:
        # The spur node ranges from the first node to the next to last node in the previous (k+1)-shortest path.
        for i in range(len(A[k]['node'])-1):
            H = MultiGraph.copy()
            # Spur node is retrieved from the previous k-shortest path, k âˆ’ 1.
            spur_node = A[k]['node'][i]
            # The sequence of nodes from the source to the spur node of the previous k-shortest path.
            root_path_nodes = A[k]['node'][:i+1]
            root_path_edges = A[k]['edge'][:i]

            for path in A:
                if root_path_edges == path['edge'][:i]:
                    # Remove the links that are part of the previous shortest paths which share the same root path.
                    # remove p.edge(i,i + 1) from Graph;
                    tail, head, key = path['edge'][i]
                    if head in H[tail] and key in H[tail][head]:
                        H.remove_edge(tail, head, key=key)

            # for each node rootPathNode in rootPath except spurNode:
            #     remove rootPathNode from Graph;
            for edge in root_path_edges:
                tail, head, key = edge
                H.remove_edge(tail, head, key=key)

            try:
                # Calculate the spur path from the spur node to the sink.
                spur_path_nodes, spur_path_edges = shortest_path_bf(H, spur_node, target, weight)
                # Entire path is made up of the root path and spur path.
                total_path_nodes = root_path_nodes + spur_path_nodes[1:]
                total_path_edges = root_path_edges + spur_path_edges
                # Add the potential k-shortest path to the heap.
                total_path_len = sum(MultiGraph[tail][head][key][weight] for tail, head, key in total_path_edges)
                # total_path_len = sum(weights[weight] for _, _, weights in total_path_edges)
                if (total_path_len, total_path_nodes, total_path_edges) not in B:
                    heappush(B, (total_path_len, total_path_nodes, total_path_edges))
            except:
                pass

        if not B:
            # This handles the case of there being no spur paths, or no spur paths left.
            # This could happen if the spur paths have already been exhausted (added to A),
            # or there are no spur paths at all - such as when both the source and sink vertices
            # lie along a "dead end".
            break
        # Add the lowest cost path becomes the k-shortest path.
        path_data = heappop(B)
        A.append({'node': path_data[1], 'edge': path_data[2]})
        yield path_data[1], path_data[2]
        k = k+ 1
