from heapq import heapify, heappop


class Heap():
    # data format: [node_degree, node_index]
    heap = []
    hash = dict()

    def init(self, initial):
        self.heap = initial
        for value, index in initial:
            self.hash[index] = value
        self.rebuild()

    def rebuild(self):
        heapify(self.heap)

    def pop(self):
        return heappop(self.heap)

    def contains(self, index):
        return index in self.hash
        
    def update(self, index, value):
        self.hash[index] = value
        for i, e in enumerate(self.heap):
            if e[1] == index:
                self.heap[i] = [value, index]
                break
        self.rebuild()

    def get(self, index):
        return self.hash.get(index)
    
    def size(self):
        return len(self.heap)


def build_heap(graph):
    heap = Heap()
    degree_index = {}

    data = []  # data format: [node_degree, node_index]
    for node in graph.nodes:
        node_index = node
        degree = graph.degree[node_index]
        degree_index[node_index] = degree
        # multiply to -1 for desc order
        data.append([-1 * degree, node_index])
    heap.init(data)

    return heap, degree_index


def get_degrees(graph):
    degrees = {}

    for node in graph.nodes:
        node_index = node
        degree = graph.degree[node_index]
        degrees[node_index] = degree
    
    return degrees


def get_heap(nodes, degrees, visited):
    heap = Heap()
    heap_data = []  # data format: [node_degree, node_index]
    for node in nodes:
        if not visited[node]:
            degree = degrees[node]
            # multiply to -1 for desc order
            heap_data.append([-1 * degree, node])
    heap.init(heap_data)

    return heap
