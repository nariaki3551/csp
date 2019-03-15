from random import randint, random
import networkx as nx
import matplotlib.pyplot as plt

N = 1500 # 点数
M = 100000 # 枝数


G = nx.DiGraph()
G.add_nodes_from(range(N))
while len(G.edges()) < M:
    u = randint(0, N-1)
    v = randint(0, N-1)
    if u == v or (u, v) in G.edges():
        continue
    G.add_edge(u, v, weight=10*random(), cost=10*random())
print('nodes')
# pos = nx.spring_layout(G)
for i in range(N):
    # print(i, *pos[i])
    print(i, random()*N, random()*N)
print('edges')
for u, v in G.edges():
    weight = G[u][v]['weight']
    cost   = G[u][v]['cost']
    print(u, v, weight, cost, sep=',')
# nx.draw(G)
# plt.show()
