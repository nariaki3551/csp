# coding: utf-8
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from collections import deque, defaultdict
from math import log2, floor, log

class Node:
    def __init__(self, name, delta, parent, ix):
        self.name   = name
        self.value  = delta
        self.parent = parent
        self.ix     = ix
        self.left   = None
        self.right  = None
        self.h_out  = None

    # 表示
    def __str__(self):
        return f"name: {self.name}, value: {self.value}, ix: {self.ix}"

# 巡回 (ジェネレータバージョン)
def traverse_node(node):
    if node:
        yield node
        for x in traverse_node(node.left):
            yield x
        for x in traverse_node(node.right):
            yield x
        for x in traverse_node(node.h_out):
            yield x

# 二分木
class BinaryTree:
    def __init__(self):
        self.root = None
        self.num  = 0 # データ個数

    # 探索
    def search(self, x):
        return node.search(self.root, x)

    # 挿入
    def insert(self, name, delta):
        if self.root is None:
            self.root = Node(name, delta, None, 0)
        else:
            node_ix = self.num
            dircs = []
            while node_ix > 0:
                dircs.append(node_ix%2) # 0 -> right, 1 -> left
                node_ix = (node_ix-1) // 2
            # 一旦heap treeに挿入
            curr_node = self.root
            for dirc in dircs[:0:-1]: # 0indexを除いて, 最後から順に
                if dirc:
                    curr_node = curr_node.left
                else:
                    curr_node = curr_node.right
            if dircs[0]:
                curr_node.left  = Node(name, delta, curr_node, self.num)
                curr_node = curr_node.left
            else:
                curr_node.right = Node(name, delta, curr_node, self.num)
                curr_node = curr_node.right

            # 上に持ち上げ
            for dirc in dircs[::-1]:
                if curr_node.parent is None\
                or curr_node.value >= curr_node.parent.value:
                    break
                # linkの付け替え
                parent = curr_node.parent
                # 2 curr - parent.parent
                if parent.parent is not None:
                    if parent.ix % 2:
                        parent.parent.left  = curr_node
                    else:
                        parent.parent.right = curr_node
                if parent.parent is not None:
                    curr_node.parent   = parent.parent
                else:
                    curr_node.parent   = None
                    self.root = curr_node
                parent.parent = curr_node

                parent_right_child = parent.right
                parent_left_child  = parent.left
                parent.right  = curr_node.right
                parent.left   = curr_node.left
                # 3
                if curr_node.right is not None:
                    curr_node.right.parent = parent
                if curr_node.left is not None:
                    curr_node.left.parent  = parent
                # 1, 4
                if curr_node.ix % 2:
                    curr_node.right  = parent_right_child
                    curr_node.left   = parent
                    if parent_right_child is not None:
                        parent_right_child.parent = curr_node
                else:
                    curr_node.left  = parent_left_child
                    curr_node.right = parent
                    if parent_left_child is not None:
                        parent_left_child.parent = curr_node
                parent.ix, curr_node.ix = curr_node.ix, parent.ix
        self.num = self.num + 1

    def root_insert(self, name, delta):
        root_node = Node(name, delta, None, 0)
        if self.root is not None:
            root_node.left = self.root
            self.root.parent = root_node
        self.root = root_node
        self.num = self.num + 1

    def h_out_insert(self, other_tree):
        if self.root is None or other_tree.root is None:
            return
        for node in self.traverse():
            if node.name == other_tree.root.name:
                break
        node.h_out = other_tree.root.left
        if other_tree.root.left is not None:
            other_tree.root.left.parent = node

    def traverse(self):
        if self.root is not None:
            for x in traverse_node(self.root):
                yield x

    def tree2graph(self):
        G = nx.DiGraph()
        # edges
        edges = defaultdict(list)
        # que (node, depth)
        que = deque([(self.root, 1)])
        while que:
            node, depth = que.popleft()
            pos_node_x, _ = pos[node.name]
            labels[node.name] = f"{node.name} ({node.value})"
            if node.left is not None:
                pos_x = pos_node_x - 2**(l-depth-1)
                pos[node.left.name] = (pos_x, l-depth-1)
                edges[node.name].append(node.left.name)
                que.append((node.left, depth+1))
            if node.right is not None:
                pos_x = pos_node_x + 2**(l-depth-1)
                pos[node.right.name] = (pos_x, l-depth-1)
                edges[node.name].append(node.right.name)
                que.append((node.right, depth+1))


    def draw_tree(self, title=None, ax=None):
        if self.root is None:
            return
        # 層数
        l = floor(log2(self.num)) + 1
        # ノード: 位置
        pos = {self.root.name: (2**(l-1)-1, l-1)}
        # ラベル
        labels = dict()
        # edges
        edges = defaultdict(list)
        # que (node, depth)
        que = deque([(self.root, 1)])
        while que:
            node, depth = que.popleft()
            pos_node_x, _ = pos[node.name]
            labels[node.name] = f"{node.name} ({node.value})"
            if node.left is not None:
                pos_x = pos_node_x - 2**(l-depth-1)
                pos[node.left.name] = (pos_x, l-depth-1)
                edges[node.name].append(node.left.name)
                que.append((node.left, depth+1))
            if node.right is not None:
                pos_x = pos_node_x + 2**(l-depth-1)
                pos[node.right.name] = (pos_x, l-depth-1)
                edges[node.name].append(node.right.name)
                que.append((node.right, depth+1))

        G = nx.DiGraph(edges)
        G.add_node(self.root.name)

        if ax is None:
            fig, ax = plt.subplots()
        ax.yaxis.set_major_locator(ticker.NullLocator()) # 軸のメモリを消す
        ax.xaxis.set_major_locator(ticker.NullLocator())

        nx.draw_networkx_nodes(G, pos, node_size=1000, node_color='mediumseagreen', node_shape='o', alpha=0.8, ax=ax)
        nx.draw_networkx_edges(G, pos, width=1.0, edge_color='k', arrowstyle='-|>', arrowsize=30, ax=ax)
        nx.draw_networkx_labels(G, pos, labels=labels, font_size=10, font_color='k',font_weight='normal', alpha=1.0, ax=ax)

        if title is not None:
            ax.set_title(title)

        return


    def draw_tree2(self, title=None):
        if self.root is None:
            return
        # ノード数
        num_nodes = sum(1 for x in self.traverse())
        # 層数
        l = floor(log(num_nodes, 3)) + 1
        # ノード: 位置
        pos = {self.root.name: (3*(3**(l-1)-1/2), l-1)}
        # ラベル
        labels = dict()
        # edges
        edges = defaultdict(list)
        # que (node, depth)
        que = deque([(self.root, 1)])
        while que:
            node, depth = que.popleft()
            pos_node_x, _ = pos[node.name]
            labels[node.name] = f"{node.name} ({node.value})"
            if node.left is not None:
                pos_x = pos_node_x - 3**(l-depth-1)
                pos[node.left.name] = (pos_x, l-depth-1)
                edges[node.name].append(node.left.name)
                que.append((node.left, depth+1))
            if node.right is not None:
                pos_x = pos_node_x + 3**(l-depth-1)
                pos[node.right.name] = (pos_x, l-depth-1)
                edges[node.name].append(node.right.name)
                que.append((node.right, depth+1))
            if node.h_out is not None:
                pos_x = pos_node_x
                pos[node.h_out.name] = (pos_x, l-depth-1)
                edges[node.name].append(node.h_out.name)
                que.append((node.h_out, depth+1))

        G = nx.DiGraph(edges)
        G.add_node(self.root.name)
        fig, ax = plt.subplots()
        ax.yaxis.set_major_locator(ticker.NullLocator()) # 軸のメモリを消す
        ax.xaxis.set_major_locator(ticker.NullLocator())

        if self.root is None:
            return

        nx.draw_networkx_nodes(G, pos, node_size=1400, node_color='mediumseagreen', node_shape='o', alpha=0.8, ax=ax)
        nx.draw_networkx_edges(G, pos, width=1.0, edge_color='k', arrowstyle='-|>', arrowsize=30)
        nx.draw_networkx_labels(G, pos, labels=labels, font_size=12, font_color='k',font_weight='normal', alpha=1.0, ax=ax)

        if title is not None:
            ax.set_title(title)

# テスト
if __name__ == '__main__':
    a = BinaryTree()
    a.insert('A', 2)
    a.insert('B', 3)
    a.insert('C', 4)
    # a.draw_tree()
    a.insert('E', 1)
    # a.draw_tree()
    a.insert('F', 3)
    a.insert('G', 8)
    a.insert('H', 0)
    a.insert('I', 7)
    a.insert('J', 4)
    a.insert('K', 1)
    a.insert('L', 10)
    a.insert('M', 0)
    a.insert('N', 4)
    a.insert('O', 100)
    # a.draw_tree()
    for x in traverse_node(a.root):
        print(x)
    a.draw_tree()

    
