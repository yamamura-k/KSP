class Binaryheap:
    class Node:
        
        def __init__(self, val=None, name=None, ix=None, tree=None) -> None:
            self.name   = name
            self.val    = val
            self.ix     = ix
            self.tree   = tree
    
        def __str__(self):
            return f"[name: {self.name}, val: {self.val}, ix: {self.ix}]"
        
        def __repr__(self) -> str:
            return self.__str__()
    def __init__(self) -> None:
        self.heap, self.root, self.size = [], None, 0

    def __insert(self, name, val, tree=None) -> None:
        x = self.Node(name=name, val=val, tree=tree)
        self.heap.append(x)
        self.size += 1
        if self.root == None:x.ix=self.size-1;self.root=x;return
        self.heap[-1].ix = self.size-1
        self.heapify()
    
    def push(self, val=-1, name=None, tree=None) -> None:
        self.__insert(name, val, tree=tree)
        
    def pop(self) -> Node:
        assert self.size > 0
        minimum_Node = self.heap[0]
        self.heap = self.heap[1:]
        self.size -= 1
        self.heapify()
        return minimum_Node
    
    def add_root(self, name, val) -> None:
        self.heap = [self.Node(name=name, val=val, ix=0)]+self.heap
        self.root = self.heap[0]
        self.__min_heapify(0)
    
    def __min_heapify(self, i : int) -> None:
        left = 2 * i + 1
        right = 2 * i + 2
        length = self.size
        smallest = i
        if left < length and self.heap[i].val > self.heap[left].val:
            smallest = left
        if right < length and self.heap[smallest].val > self.heap[right].val:
            smallest = right
        if smallest != i:
            self.__swap(i, smallest)
            self.__min_heapify(smallest)
    
    def __swap(self, i : int, j : int) -> None:
        self.heap[i].ix,self.heap[j].ix         = self.heap[j].ix,self.heap[i].ix
        self.heap[i], self.heap[j]              = self.heap[j], self.heap[i] 

    def heapify(self) -> None:
        for i in reversed(range(self.size//2)):
            self.__min_heapify(i)
    
    def __bool__(self):
        return self.size != 0