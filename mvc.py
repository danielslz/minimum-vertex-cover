import jgrapht
import sys
import utils

from heap import build_heap, get_degrees, get_heap


def minimum_vertex_cover_greedy(graph):
    mvc = set()

    edges = set(graph.edges)
    heap, degrees = build_heap(graph)

    while len(edges) > 0:
        # remove node with max degree
        _, node_index = heap.pop()
        adj = set(graph.edges([node_index]))
        for u, v in adj:
            # remove edge from list
            edges.discard((u, v))
            edges.discard((v, u))

            # update neighbors
            if heap.contains(v):
                new_degree = degrees[v] - 1
                # update index
                degrees[v] = new_degree
                # update heap
                heap.update(v, -1 * new_degree)

        # add node in mvc
        mvc.add(node_index)

    return mvc


def minimum_vertex_cover_approximation(graph):
    mvc = set()

    edges = set(graph.edges)
    nodes = set(graph.nodes)

    while len(edges) > 0:
        # pick any node
        node = nodes.pop()
        for u, v in graph.edges([node]):
            # remove edge from list
            edges.discard((u, v))
            edges.discard((v, u))
        # add node in mvc
        mvc.add(node)

    return mvc


def remove_edges_and_update_degrees(edges_to_remove, edges, degrees, visited):
    for u, v in edges_to_remove:
        # remove edge from list
        edges.discard((u, v))
        edges.discard((v, u))
        # update degree
        degrees[v] -= 1
        if degrees[v] == 0:
            visited[v] = True


def minimum_vertex_cover_hybrid_greedy(graph):
    mvc = set()
    visited = {}

    degrees = get_degrees(graph)
    edges = set(graph.edges)
    nodes = set(graph.nodes)

    # mark node with degree 1 as visited, otherwise not visited
    for node in nodes:
        # init status
        visited[node] = False
        if degrees[node] == 1:
            # mark node as visited
            visited[node] = True
            # remove edges and update node degrees
            for u, v in graph.edges([node]):
                if degrees[v] > 1:
                    # remove edge from list
                    edges.discard((u, v))
                    edges.discard((v, u))
                    # update degree
                    degrees[v] -= 1
                    if degrees[v] == 0:
                        visited[v] = True

    # build heap with nodes not visited
    heap = get_heap(nodes, degrees, visited)

    # heap update factor
    heap_update_factor = sys.maxsize
    total_nodes = heap.size()
    ratio = total_nodes / len(edges)
    if len(nodes) > 100:
        heap_update_factor = int(total_nodes * ratio)

    # greedy
    count = 0
    while(len(edges) > 0):
        count += 1
        # verify if must update heap
        if count > heap_update_factor:
            count = 0
            # build heap with nodes not visited
            heap = get_heap(nodes, degrees, visited)

        try:
            _, node_index = heap.pop()
            if not visited[node_index]:
                visited[node_index] = True
                mvc.add(node_index)
                # remove edges
                remove_edges_and_update_degrees(graph.edges([node_index]), edges, degrees, visited)
        except IndexError:
            # no more nodes
            break

    return mvc


### RUN TESTS

our_methods = [
    (minimum_vertex_cover_approximation, 'Approximation'),
    (minimum_vertex_cover_greedy, 'Tradicional Greedy'),
    (minimum_vertex_cover_hybrid_greedy, 'Hybrid Greedy')
]

lib_methods = [
    (jgrapht.algorithms.vertexcover.greedy, 'Jgrapht Greedy'),
    (jgrapht.algorithms.vertexcover.edgebased, 'Jgrapht Edgebased'),
    (jgrapht.algorithms.vertexcover.clarkson, 'Jgrapht Clarkson'),
    (jgrapht.algorithms.vertexcover.baryehuda_even, 'Jgrapht Baryehuda_even'),
    # (jgrapht.algorithms.vertexcover.exact, 'Jgrapht Exact'),
]

utils.run_tests(our_methods, lib_methods, utils.BHOSLIB_GRAPH, write_csv=True)


### RUN STANDALONE

# # build graph
# g = utils.create_graph_from_file('data/bhoslib/frb30-15-1.mis', graph_format=utils.DIMACS_GRAPH)
# jg = utils.nx_to_jgraph(g)

# print(f'No of nodes: {g.number_of_nodes()}')
# print(f'No of edges: {g.number_of_edges()}')
# print('----')

# # calculate mvc
# utils.run(our_methods, g)

# print('-----')
# utils.run(lib_methods, jg, is_jgrapht=True)

# # plot
# utils.plot_graph(g)
