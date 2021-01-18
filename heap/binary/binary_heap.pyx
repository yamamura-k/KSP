from collections import deque
class Binaryheap:
    class Node:
        
        def __init__(self, val=None, name=None, ix=None, tree=None) -> None:
            self.name  = name
            self.val   = val
            self.ix    = ix
            self.tree  = tree
            self.left  = None
            self.right = None
        
        def haveTree(self):
            if self.tree != None and self.tree.size > 0:
                return True
            return False

        def __str__(self):
            return f"[name: {self.name}, val: {self.val}, ix: {self.ix}]"
        
        def __repr__(self) -> str:
            return self.__str__()

    def __init__(self) -> None:
        self.heap, self.root, self.size = [], None, 0

    def __insert(self, name, val, tree=None) -> None:
        self.size += 1
        x = self.Node(name=name, val=val, tree=tree)
        x.ix = self.size-1
        if self.root is None:
            self.root = x
        p = x.ix//2
        if x.ix%2==0:
            p -= 1
        self.heap.append(x)
        if 2*p+1 == x.ix:
            self.heap[p].left = x
        elif 2*p+2 == x.ix:
            self.heap[p].right = x
        self.heapify()
        self.root = self.heap[0]
    
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
        self.__insert(name, val)
        self.root = self.heap[0]
    
    def __min_heapify(self, i : int) -> None:
        cdef int left
        cdef int right
        cdef int smallest
        cdef int length
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
        if i > j:
            i, j = j, i
        if j == 2*i+1:# 左の子
            self.heap[i].right, self.heap[j].right = self.heap[j].right, self.heap[i].right
            self.heap[i].left = self.heap[j].left
            self.heap[j].left = self.heap[i]
        elif j == 2*i+2:
           self.heap[i].left, self.heap[j].left = self.heap[j].left, self.heap[i].left
           self.heap[i].right = self.heap[j].right
           self.heap[j].right = self.heap[i]
        self.heap[i].ix, self.heap[j].ix = self.heap[j].ix,self.heap[i].ix
        self.heap[i], self.heap[j]       = self.heap[j], self.heap[i] 

    def heapify(self) -> None:
        cdef int i
        for i in reversed(range(self.size//2+1)):
            self.__min_heapify(i)
    
    def __bool__(self):
        return self.size != 0
    
    def __len__(self):
        return self.size
    
    def traverse(self):
        """
        Return : Node
        """
        return self.__bfs(self.heap)
    
    def __bfs(self, heap):
        length = len(heap)
        if length == 0:return []
        q = deque([0])
        while q:
            u = q.popleft()
            yield heap[u]
            left  = 2*u+1
            right = 2*u+2
            if heap[u].haveTree():
                yield self.__bfs(heap[u].tree.heap)
            if left < length:
                q.append(left)
            if right < length:
                q.append(right)

    def h_out_insert(self, other):
        if not (self.root and other.root):return
        for node in self.traverse():
            if node.name == other.root.name:
                node.tree = other.root.left
                break