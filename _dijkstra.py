from testtools import timer
from heap import fibonacci_heap as heap
#from heap import binary_heap as heap
from collections import defaultdict

class my_dict(defaultdict):
    def __init__(self, name_type) -> None:
        super().__init__(name_type)
    
    def free(self) -> None:
        vals = list(self.vals())
        while vals:
            val = vals.pop()
            del self[val]

class Dijkstra:
    def __init__(self):
        self.__adj      = None
        #self.__edg2Node = dict()
        self.__que      = heap.FibonacciHeap()
        #self.__que      = heap.Binaryheap()
        self.distances  = my_dict(lambda : self.INF)
        self.__visited  = my_dict(lambda : False)
        self.prev       = my_dict(lambda : None)
        self.INF        = float('inf')
    
    def set_edges(self, edges : dict) -> None:
        """
        Input : 要素が (長さ,ノードid) のような形式の隣接リストを期待
        """
        self.__adj = edges

    def reset(self) -> None:
        self.__adj.free()
        self.__que.clear()
        self.distances.free()
        self.__visited.free()
    
    @timer
    def dijkstra_with_fibonacci_heap(self, source, target = None) -> None:
        self.__que.push(0,source)
        #self.__edg2Node[source] = self.__que.push(0,source)
        self.distances[source] = 0
        while self.__que:
            _from = self.__que.pop().name
            #del self.__edg2Node[_from]
            if self.__visited[_from]:continue
            self.__visited[_from] = True
            if _from not in self.__adj:continue
            __adjacent = self.__adj[_from]
            dist = self.distances[_from]
            for v in __adjacent:
                cost, to = v
                if self.__visited[to]:continue
                if dist + cost < self.distances[to]:
                    new_dist = dist + cost
                    self.prev[to]      = _from
                    self.__que.push(new_dist, to)
                    """
                    if to not in self.__edg2Node:
                        self.__edg2Node[to] = self.__que.push(new_dist, to)
                    else:
                        self.__que.decrease_val(self.__edg2Node[to], new_dist)
                    #"""
                    self.distances[to] = new_dist

    def dijkstra(self, source, target = None) -> None:
        return self.dijkstra_with_fibonacci_heap(source, target)
            
    
    def dist2list(self):
        m = max(self.distances.vals())+1
        dists = [self.INF]*m
        for i in self.distances:
            dists[i] = self.distances[i]
        return dists

    def __debug(self):
        print(self.__adj.items())
        print(self.__que.size)
        print(self.__visited.items())