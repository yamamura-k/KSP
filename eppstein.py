from _dijkstra import Dijkstra
from heap import binary_heap as heap
import networkx as nx
from copy import deepcopy
from heapq import heappop, heappush

class SPT:
    def __init__(self, nodes, prev) -> None:
        E = set()
        V = set()
        for node in nodes:
            if prev[node] is None:continue
            V.add(node)
            while prev[node] is not None:
                E.add((prev[node], node))
                node = prev[node]
        self.edges  = list(E)
        self.vertex = list(V)

class eppstein:
    def __init__(self, G, source, target, k=1) -> None:
        self.G        = G
        self.source   = source
        self.target   = target
        self.k        = k
        self.T        = None
        self.P        = None
        self.distance = None
    
    def __preprocess(self):
        """
        STEP 1 : Construct the shortest paths tree
        STEP 2 : Construct H_out, H_T, H_G
        STEP 3 : Construct a path graph P_G
        """
        # 与えられたグラフを逆向きにして、targetを始点とする最短路木を構成する
        # 自作モジュールで実装
        r_edges = dict()
        for edge in self.G.edges():
            u, v = edge
            cost = self.G[u][v]["weight"]
            if v not in r_edges:
                r_edges[v] = []
            r_edges[v].append((cost, u))
        dj = Dijkstra()
        dj.set_edges(r_edges)
        dj.dijkstra(self.target)
        self.distance = dj.distances
        tmp= SPT(self.G.nodes(), dj.prev)
        self.T = self.G.edge_subgraph([(x[1], x[0])for x in tmp.edges])
        """# networkxを使った実装
        pred, distance = nx.dijkstra_predecessor_and_distance(G.reverse(), source=target)
        # shortest path tree
        self.T = G.edge_subgraph((i, pred[i][0]) for i in pred if pred[i])
        self.distance = distance
        """

        # Construct Binary Heap "H_out"
        H_out = dict()
        for v in self.G:
            h_out = heap.Binaryheap()
            out_edges = self.__out_edges(v)
            if out_edges:
                max_root, *other_edges = out_edges
                for edge in other_edges:
                    h_out.push(self.__delta(edge), edge)
                h_out.add_root(max_root, self.__delta(max_root))

            H_out[v] = h_out

        # Construct 3 Heap "H_T"
        H_T = dict()
        h_t = heap.Binaryheap()
        out_root = H_out[self.target].root
        if out_root:
            h_t.push(out_root.val, out_root.name)
        H_T[self.target] = h_t
        for edge in nx.bfs_edges(self.T.reverse(), source=self.target):
            h_t = deepcopy(H_T[edge[0]])
            out_root = H_out[edge[1]].root
            if out_root:
                h_t.push(out_root.val, out_root.name)
            H_T[edge[1]] = h_t
        
        # Construct 4 Heap "H_G" simlutaneously
        H_G = dict()
        h_g = deepcopy(H_T[self.target])
        h_g.h_out_insert(H_out[self.target])
        H_G[self.target] = h_g
        for edge in nx.bfs_edges(self.T.reverse(), source=self.target):
            _, child = edge
            h_g = H_T[child]
            if len(h_g.heap) > 0:
                out_root = H_out[child].root
                for v in nx.shortest_path(self.T, source=child, target=self.target):
                    h_g.h_out_insert(H_out[v])
            H_G[child] = h_g
        
        # Construct a Path Graph
        P = nx.DiGraph()
        
        # add heap edges
        self.__add_H_G_to_P(P, H_G, self.target)
        for edge in nx.bfs_edges(self.T.reverse(), source=self.target):
            _, child = edge
            self.__add_H_G_to_P(P, H_G, child)
        
        # add cross edges
        for v in P:
            _, edge = v
            if edge not in self.T:
                _, w = edge
                if H_G[w].root:
                    u_name = (w, H_G[w].root.name)
                    weight = self.__delta(H_G[w].root.name)
                    P.add_edge(v, u_name, weight=weight, edge_type="cross_edge")
        
        # add root node
        P.add_node("RootNode")
        u = (self.source, H_G[self.source].root.name)
        weight = self.__delta(H_G[self.source].root.name)
        P.add_edge("RootNode", u, weight=weight, edge_type="root_edge")
        self.P = P

    def find_k_shortest(self):
        minus_weight = -sum(abs(self.T.edges()[edge]["weight"])for edge in self.T.edges())
        Paths = []
        Q = [(0, ["RootNode"])]
        k = 0
        shortest_path_length = 0
        lengths = []
        while Q and k < self.k:
            potential, sidetracks = heappop(Q)
            Paths.append(self.__sidetrack2path(sidetracks, minus_weight))
            last_sidetrack = sidetracks[-1]
            for v in self.P[last_sidetrack]:
                new_potential = potential + self.P.edges()[last_sidetrack, v]["weight"]
                new_sidetracks = sidetracks + [v]
                heappush(Q, (new_potential, new_sidetracks))
            k += 1
            if k == 1:
                shortest_path_length = sum(self.G[u][v]["weight"]for u, v in zip(Paths[-1], Paths[-1][1:]))
            length = shortest_path_length + potential
            lengths.append(length)
        return Paths, lengths

    def __sidetrack2path(self, sidetracks, minus_weight):
        tmp_T = self.T.copy()
        for u, v in zip(sidetracks[1:], sidetracks[2:]):
            if self.P[u][v]["edge_type"] == "cross_edge":
                tmp_T.add_edge(*u[1], weight=minus_weight)
        if len(sidetracks) > 1:
            last_sidetracks = sidetracks[-1]
            tmp_T.add_edge(*last_sidetracks[1], weight=minus_weight)
        return nx.shortest_path(tmp_T, source=self.source, target=self.target, weight="weight")
        
    def __add_H_G_to_P(self, P, H_G, node):
        for v in H_G[node].traverse():
            v_name = (node, v.name)
            v_delta = self.__delta(v.name)
            P.add_node(v_name)
            if v.left:
                u_name = (node, v.left.name)
                if (v_name, u_name) not in P.edges():
                    weight = self.__delta(v.left.name) - v_delta
                    P.add_edge(v_name, u_name, weight=weight, edge_type="heap_edge")
            if v.right:
                u_name = (node, v.right.name)
                if (v_name, u_name) not in P.edges():
                    weight = self.__delta(v.right.name) - v_delta
                    P.add_edge(v_name, u_name, weight=weight, edge_type="heap_edge")
            if v.haveTree():
                vout_name = v.tree.root.name
                u_name = (node, vout_name)
                if (v_name, u_name) not in P.edges():
                    weight = self.__delta(vout_name) - v_delta
                    P.add_edge(v_name, u_name, weight=weight, edge_type="heap_edge")
    
    """# 例外処理用。使わないでしょう。
    from typing import Generator
    def __add_to_P(self, P, generator, node):
        for v in generator:
            if isinstance(v, Generator):
                P = self.__add_to_P(P, v, node)
                continue
            v_name = (node, v.name)
            v_delta = self.__delta(v.name)
            P.add_node(v_name)
            if v.left:
                u_name = (node, v.left.name)
                if (v_name, u_name) not in P.edges():
                    weight = self.__delta(v.left.name) - v_delta
                    P.add_edge(v_name, u_name, weight=weight, edge_type="heap_edge")
            if v.right:
                u_name = (node, v.right.name)
                if (v_name, u_name) not in P.edges():
                    weight = self.__delta(v.right.name) - v_delta
                    P.add_edge(v_name, u_name, weight=weight, edge_type="heap_edge")
            if v.haveTree():
                vout_name = v.tree.root.name
                u_name = (node, vout_name)
                if (v_name, u_name) not in P.edges():
                    weight = self.__delta(vout_name) - v_delta
                    P.add_edge(v_name, u_name, weight=weight, edge_type="heap_edge")
    """

    def __out_edges(self, v):
        if v in self.T:
            return sorted([(v, head) for head in self.G[v] if head not in self.T[v]])
        return sorted([(v, head) for head in self.G[v]])

    def __delta(self, edge):
        tail, head = edge
        return self.G[tail][head]["weight"] + self.distance[head] -self.distance[tail]
    
    def test(self):
        self.__preprocess()
        from matplotlib import pyplot as plt
        pos = nx.shell_layout(self.P)
        nx.draw_networkx_nodes(self.P, pos, node_color='b',alpha=0.6)
        nx.draw_networkx_labels(self.P, pos)
        nx.draw_networkx_edges(self.P, pos)
        for edge in self.P.edges():
            if self.P.edges[edge]['edge_type'] == 'heap_edge':
                nx.draw_networkx_edges(self.P, pos, edgelist=[edge], width=1.0, edge_color='k', arrowstyle='-|>', arrowsize=30)
            if self.P.edges[edge]['edge_type'] == 'cross_edge':
                nx.draw_networkx_edges(self.P, pos, edgelist=[edge], width=1.0, edge_color='r', arrowstyle='-|>', arrowsize=30)
            if self.P.edges[edge]['edge_type'] == 'root_edge':
                nx.draw_networkx_edges(self.P, pos, edgelist=[edge], width=1.0, edge_color='g', arrowstyle='-|>', arrowsize=30)
        plt.axis('off')
        plt.savefig("./test/path_graph.pdf")
        plt.close()
        paths, lengths = self.find_k_shortest()
        pos = nx.shell_layout(self.G)
        for path, length in zip(paths, lengths):
            nx.draw_networkx_labels(self.G, pos)
            nx.draw_networkx_nodes(self.G, pos, node_color='b',alpha=0.6)
            nx.draw_networkx_edges(self.G, pos)
            edges = [(x, y) for x, y in zip(path[:-1], path[1:])]
            nx.draw_networkx_edges(self.G, pos, edgelist=edges, edge_color="r", alpha=0.6)
            plt.axis('off')
            plt.savefig(f"./test/shortest_length{length}.pdf")
            plt.close()


            

if __name__ == "__main__":
    # test configuration
    edges = {'C': {'D': {'weight': 3}, 'E': {'weight': 2}},
             'D': {'E': {'weight': 2}, 'F': {'weight': 4}},
             'E': {'F': {'weight': 2}, 'G': {'weight': 3}},
             'F': {'H': {'weight': 2}, 'G': {'weight': 3}},
             'G': {'H': {'weight': 2}}}
    pos = {'C': (0, 1),
           'D': (1, 1),
           'E': (1, 0),
           'F': (2, 1),
           'G': (2, 0),
           'H': (3, 0)}
    G = nx.DiGraph(edges)
    source = 'C'
    target = 'H'
    K  = 100

    ep = eppstein(G, source, target, k=K)
    ep.test()