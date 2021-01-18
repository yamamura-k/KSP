#import cython
class FibonacciHeap:
    class Node:
        """
        """
        def __init__(self, val=-1, name=None) -> None:
            self.val = val
            self.name = name
            self.parent = None
            self.child = None
            self.left  = None
            self.right = None
            self.degree = 0
            self.damaged = False
        
        def add_child(self, x : object) -> None:
            """Add child node to self
            """
            if self.child is None:
                self.child = x
                x.right, x.left = x, x
            else:
                right_to_child = self.child.right
                self.child.right = x
                x.left = self.child
                x.right = right_to_child
                self.child.right.left = x
            self.child = x
            x.parent = self
            x.damaged = False
            self.degree += 1
        
        def remove_child(self, x : object) -> None:
            """Remove child node x from self
            """
            if self.child is None:raise(ValueError)
            elif self.degree == 1:self.child = None
            else:
                if self.child is x:self.child = x.right
                left_to_x, right_to_x = x.left, x.right
                left_to_x.right = right_to_x
                right_to_x.left = left_to_x
            self.degree -= 1
        
        def __str__(self) -> str:
            return str(self.name)
        
        def __repr__(self) -> str:
            return self.__str__()

    def __init__(self) -> None:
        self.total_nodes = 0
        self.total_trees = 0
        self.min_node = None
    
    def __add_root(self, x : Node) -> None:
        if self.min_node is None:
            x.left, x.right =x, x
        else:
            right_to_min = self.min_node.right
            self.min_node.right = x
            x.left  = self.min_node
            x.right = right_to_min
            right_to_min.left = x
        self.total_trees += 1
    
    def __remove_root(self, x : Node) -> None:
        right_to_x, left_to_x = x.right, x.left
        right_to_x.left = left_to_x
        left_to_x.right = right_to_x
        self.total_trees -= 1
    
    def __insert(self, x : Node) -> Node:
        if self.min_node is None:
            self.__add_root(x)
            self.min_node = x
        else:
            self.__add_root(x)
            if x.val < self.min_node.val:
                self.min_node = x
        self.total_nodes += 1
        return x
    
    def __consolidate(self) -> None:
        A = [None] * self.total_nodes
        root = self.min_node
        for _ in range(self.total_trees):
            x = root
            root = root.right
            _d = d = x.degree
            for i in range(_d, self.total_nodes):
                d = i
                if A[d] is None:break
                y = A[d]
                if x.val > y.val:
                    x, y = y, x
                self.__link(y, x)
                A[d] = None
            try:A[d] = x
            except IndexError:breakpoint()
        self.min_node = None
        for i in range(self.total_nodes):
            if A[i]:
                if self.min_node is None:
                    self.min_node = A[i]
                elif A[i].val < self.min_node.val:
                    self.min_node = A[i]
    
    def __link(self, y : Node, x : Node) -> None:
        self.__remove_root(y)
        x.add_child(y)
    
    def decrease_val(self, x : Node, val) -> None:
        x.val = min(val, x.val)
        y = x.parent
        if y and x.val < y.val:
            self.__cut(x, y)
            self.__cascading_cut(y)
        if self.min_node is None or x.val < self.min_node.val:
            self.min_node = x
    
    def __cut(self, x : Node, y : Node) -> None:# x < y
        x.damaged = False
        y.remove_child(x)
        self.__add_root(x)
        x.parent = None
    
    def __cascading_cut(self, y : Node) -> None:
        z = y.parent
        if z:
            if y.damaged:
                self.__cut(y, z)
                self.__cascading_cut(z)
            else:
                y.damaged = False
    
    def delete(self, x : Node):
        class MaskClass:
            def __lt__(self, other):
                return True
            def __gt__(self, other):
                return False
        self.__decrease_val(x, MaskClass())
        self.pop()

    def top(self) -> Node:
        return self.min_node
    
    def pop(self) -> Node:
        z = self.min_node
        if z:
            x = z.child
            d = z.degree
            for _ in range(d):
                y = x.right
                self.__add_root(x)
                x.parent = None
                x = y
            self.__remove_root(z)
            if z == z.right:
                self.min_node = None
            else:
                self.min_node = z.right
                self.__consolidate()
            self.total_nodes -= 1
        return z
    
    def search(self):
        from collections import deque, defaultdict
        from matplotlib import pyplot as plt
        import networkx as nx
        fig = plt.figure()
        queue = deque([self.min_node])
        visited = defaultdict(lambda :False)
        G = nx.DiGraph()
        while queue:
            s = queue.popleft()
            if visited[s]:continue
            visited[s] = True
            G.add_node(s.name, weight=s.val)
            if s != s.right:
                queue.append(s.right)
                G.add_node(s.right.name, weight=s.right.val)
                G.add_edge(s.name, s.right.name)
            if s.child:
                queue.append(s.child)
                G.add_node(s.child.name, weight=s.child.val)
                G.add_edge(s.name, s.child.name)
        pos = nx.spring_layout(G)
        
        node_size = [ d['weight']*20 for (n,d) in G.nodes(data=True)]
        nx.draw_networkx_nodes(G, pos, node_color='b',alpha=0.6, node_size=node_size)
        nx.draw_networkx_labels(G, pos)
        nx.draw_networkx_edges(G, pos)
        
        plt.axis('off')
        return fig
        #plt.savefig("g2.png")
        plt.show()
        plt.close()
    
    def _search(self):
        from collections import deque, defaultdict
        from matplotlib import pyplot as plt
        import networkx as nx
        fig = plt.figure()
        queue = deque([self.min_node])
        visited = defaultdict(lambda :False)
        G = nx.DiGraph()
        for k in self.node:
            s = self.node[k]
            if visited[s]:continue
            visited[s] = True
            G.add_node(s.name, weight=s.val)
            if s != s.right:
                G.add_node(s.right.name, weight=s.right.val)
                G.add_edge(s.name, s.right.name)
            if s.child:
                G.add_node(s.child.name, weight=s.child.val)
                G.add_edge(s.name, s.child.name)
        pos = nx.spring_layout(G)
        
        node_size = [ d['weight']*20 for (n,d) in G.nodes(data=True)]
        nx.draw_networkx_nodes(G, pos, node_color='b',alpha=0.6, node_size=node_size)
        nx.draw_networkx_labels(G, pos)
        nx.draw_networkx_edges(G, pos)
        
        plt.axis('off')
        return fig
        #plt.savefig("g2.png")
        plt.show()
        plt.close()




    def push(self, val, name) -> Node:
        x = self.Node(val, name)
        return self.__insert(x)
    
    def __bool__(self):
        return self.min_node is not None