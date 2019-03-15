#!/usr/bin/env python
# coding: utf-8

import networkx as nx
import matplotlib.pyplot as plt
from csv import reader as csv_reader
from collections import defaultdict
import time
from sys import argv

from Bellman_Ford import shortest_path_bf
from Yen_KSP import YenKSP
from Eppstein_KSP import EppsteinKSP


__doc__ = f"""
Usage:
    {__file__} graph_file source target upper_bound [--print_path] [--yen]

Options:
    --print_path
    --yen        : Use Yen algorithm for the k shortest path problem

Notes:
    Build Date: Mar 7 2019
    Main Algorithm            : Hander-Zang algorithm
    Shortest Path Algorithm   : Bellman-Ford algorithm
    K Shortest Path Algorithm : Eppstein algorithm
                              : Yen algorithm

Graph (Multipul Directed Graph):
    format of graph_fileis 
    tail_node,head_node,weight(float),cost(float)
"""

PRINT_PATH = False
YEN = False


def usage():
    print(__doc__)


def main(edge_file, source, target, upper_bound):
    print('Build Date: Mar 07 2019')
    print('Main Algorithm            : Hander-Zang algorithm')
    print('Shortest Path Algorithm   : Bellman-Ford algorithm')
    if YEN:
        print('K Shortest Path Algorithm : Yen algorithm')
    else:
        print('K Shortest Path Algorithm : Eppstein algorithm')
    print()

    G = read_edge_file(edge_file)
    opt_path, path_length, cost_length\
        = dual_algorithm(G, source, target, upper_bound)

    if opt_path is not None:
        print('\n\n')
        print(f'*Optimal Solution: {path_length:.2f}')
        print(f'    path {opt_path}')
        print(f'    f = {path_length:.3f}, g = {cost_length:.3f}')


def read_edge_file(edge_file):
    # read graph node - edge data
    # [node format]:  node, x position, y position
    # [edge format]: head node, tail node, objective cost, constraint cost

    G = nx.MultiDiGraph()
    edge_dict = defaultdict(list)

    with open(edge_file, 'r') as f:
        for row in csv_reader(f):
            if len(row) == 4:
                tail, head, weight, cost = row
                weight = float(weight)
                cost = float(cost)
                edge_dict[tail, head].append((weight, cost))

    for (tail, head), edges in edge_dict.items():
        for key, (weight, cost) in enumerate(edges):
            G.add_edge(tail, head, c=weight, t=cost, key=key)

    print(f'the number of nodes: {G.number_of_nodes()}')
    print(f'the number of edges: {G.number_of_edges()}')

    return G


def convert_graph_weight(G, u):
    H = nx.MultiDiGraph()
    for tail in G:
        for head, edges in G[tail].items():
            for key, weights in edges.items():
                c, t = weights['c'], weights['t']
                H.add_edge(tail, head, w=c+u*t, c=c, t=t, key=key)
    return H


def print_log_head():
    print('-'*60)
    print(f'{"Iter":>5s} {"Step":>4s} {"Update":>6s} {"Best":>7s} {"LB":>7s} {"UB":>7s} {"Gap":>7s} {"Time":>7s}')
    print('-'*60)


def print_log(step, update, iter_count, gap=None, LB=None, UB=None, time=None):
    gap = f'{"-":>6s}' if gap is None else f'{gap*100:>6.2f}'
    LB  = f'{"-":>7s}' if LB  is None else f'{LB:>7.2f}'
    UB  = f'{"-":>7s}' if UB  is None else f'{UB:>7.2f}'
    print(f'{iter_count:5d} {step:>4s} {update:>6s} {UB} {LB} {UB} {gap}% {time:6.0f}s')


def print_best_sol(best_path, path_length, cost_length):
    print(f'*Best Solution: {path_length:.2f}')
    print(f'    path {best_path}')
    print(f'    f = {path_length:.3f}, g = {cost_length:.3f}')


def dual_algorithm(G, source, target, upper_bound):
    iter_count = 0
    start_time = time.time()

    # STEP0 (shrink source - target path)
    reachable_nodes_from_source = set()
    for edge in nx.bfs_edges(G, source=source):
        tail, head = edge
        reachable_nodes_from_source |= {tail, head}
    if target not in reachable_nodes_from_source:
        print('There does not exist source {source} - target {target} path')
        return None, None, None
    reachable_nodes_to_target = set()
    for edge in nx.bfs_edges(G.reverse(), source=target):
        tail, head = edge
        reachable_nodes_to_target |= {tail, head}
    G = G.subgraph(reachable_nodes_from_source & reachable_nodes_to_target)
    
    print('\nRemove the nodes which does not contained source - target path (#STEP0)')
    print(f'remained the number of nodes: {G.number_of_nodes()}')
    print(f'remained number of edges: {G.number_of_edges()}\n')

    # STEP1 (obtain shortest pash respect to "weight")
    _, path_edges = shortest_path_bf(G, source, target, weight='c')
    path_length = sum(G[tail][head][key]['c'] for tail, head, key in path_edges)
    cost_length = sum(G[tail][head][key]['t'] for tail, head, key in path_edges) - upper_bound
    shortest_length_path = path_edges

    if cost_length <= 0:
        opt_path = path_edges
        return opt_path, path_length, cost_length+upper_bound
    else:
        opt_plus  = path_edges
        path_plus = path_length
        cost_plus = cost_length
        LB        = path_length
        print('We obtain shortest path on weight (#STEP1)')
        if PRINT_PATH: print(f'    path {path_edges}')
        print(f'    f = {path_length:.3f}, g = {cost_length:.3f}\n')

    # STEP2(obtain shortest path respect to "cost")
    _, path_edges = shortest_path_bf(G, source=source, target=target, weight='t')
    path_length = sum(G[tail][head][key]['c'] for tail, head, key in path_edges)
    cost_length = sum(G[tail][head][key]['t'] for tail, head, key in path_edges) - upper_bound
    shortest_cost_path = path_edges

    if cost_length > 0:
        print(f'We find there is not a path satisfies the constrainet')
        print(f'the minimum cost path length is {cost_length+upper_bound}')
        return None, None, None
    else:
        opt_minus  = path_edges
        path_minus = path_length
        cost_minus = cost_length
        UB         = path_length
        print('We obtain shortest path on cost (#STEP2)')
        if PRINT_PATH: print(f'    path {path_edges}')
        print(f'    f = {path_length:.3f}, g = {cost_length+upper_bound:.3f}\n')

    print(f'Best Solution: {path_minus: .3f}\n')
    u = (path_minus - path_plus) / (cost_plus - cost_minus)
    L = path_plus + u * cost_plus


    iter_count += 1
    print_log_head()
    print_log(step='#1', update='LB', iter_count=iter_count, LB=LB, time=time.time()-start_time)
    iter_count += 1
    print_log(step='#2', update='UB', iter_count=iter_count, gap=(UB-LB)/(abs(UB)-1), LB=LB, UB=UB, time=time.time()-start_time)


    # STEP3
    epsilon = 0.000001 # the terminating parametor of Step3
    while True:
        iter_count += 1
        if iter_count % 20 == 0:
            print_log_head()
        update = ""
        H = convert_graph_weight(G, u)
        _, path_edges = shortest_path_bf(H, source, target, weight='w')
        Lu = sum(H[tail][head][key]['w'] for tail, head, key in path_edges) - u * upper_bound
        path_length = sum(G[tail][head][key]['c'] for tail, head, key in path_edges)
        cost_length = sum(G[tail][head][key]['t'] for tail, head, key in path_edges) - upper_bound
        if cost_length == 0:
            return path_edges, path_length, const_length+upper_bound # find opt sol
        elif abs(Lu - L) < epsilon and cost_length < 0:
            opt_minus = path_edges
            if LB < Lu:
                update += " LB"
                LB = Lu
            if path_length < UB:
                update += " UB"
                UB = path_length
                if PRINT_PATH:
                    print_best_sol(path_edges, path_length, cost_length+upper_bound)
            print_log(step='#3', update=update, iter_count=iter_count, gap=(UB-LB)/(abs(UB)-1), LB=LB, UB=UB, time=time.time()-start_time)
            break
        elif abs(Lu - L) < epsilon and cost_length > 0:
            if LB < Lu:
                update += " LB"
            if path_minus < UB:
                update += " UB"
            LB = Lu
            UB = path_minus
            print_log(step='#3', update=update, iter_count=iter_count, gap=(UB-LB)/(abs(UB)-1), LB=LB, UB=UB, time=time.time()-start_time)
            break
        elif cost_length > 0:
            opt_plus  = path_edges
            path_plus = path_length
            cost_plus = cost_length
        elif cost_length <= 0:
            opt_minus  = path_edges
            path_minus = path_length
            cost_minus = cost_length
            if path_length < UB:
                update += " UB"
                UB = path_length
                if PRINT_PATH:
                    print_best_sol(path_edges, path_length, cost_length+upper_bound)
        u = (path_minus - path_plus) / (cost_plus - cost_minus)
        L = path_plus + u * cost_plus
        print_log(step='#3', update=update, iter_count=iter_count, gap=(UB-LB)/(abs(UB)-1), LB=LB, UB=UB, time=time.time()-start_time)

    if LB >= UB:
        return opt_minus, path_minus, cost_minus+upper_bound # find opt sol

    # STEP 4   CLOSING THE GAP
    H = convert_graph_weight(G, u)
    k_shortest_paths = EppsteinKSP(H, source, target, 'w')
    # k_shortest_paths = YenKSP(H, source, target, 'w')
    _, first_path_edges = k_shortest_paths.__next__()
    _, second_path_edges = k_shortest_paths.__next__()
    while True:
        iter_count += 1
        if iter_count % 20 == 0:
            print_log_head()
        update = ""
        try:
            _, path_edges = k_shortest_paths.__next__()
            Lu = sum(H[tail][head][key]['w'] for tail, head, key in path_edges) - u * upper_bound
            path_length = sum(G[tail][head][key]['c'] for tail, head, key in path_edges)
            cost_length = sum(G[tail][head][key]['t'] for tail, head, key in path_edges) - upper_bound
        except StopIteration:
            Lu = path_length = float('inf')
        if LB < Lu:
            update += " LB"
        LB = Lu
        if cost_length <= 0 and path_length < UB:
            UB = path_length
            opt_minus = path_edges
            path_minus = path_length
            cost_minus = cost_length
            update += " UB"
            if PRINT_PATH:
                print_best_sol(path_edges, path_length, cost_length+upper_bound)
        print_log(step='#4', update=update, iter_count=iter_count, gap=(UB-LB)/(abs(UB)-1), LB=LB, UB=UB, time=time.time()-start_time)
        if LB >= UB:
            return opt_minus, path_minus, cost_minus+upper_bound # find opt sol


if __name__ == '__main__':
    if len(argv) > 4:
        if '--print_path' in argv:
            PRINT_PATH = True
        if '--yen' in argv:
            YEN = True
        main(*argv[1:4], float(argv[4]))
    else:
        usage()
