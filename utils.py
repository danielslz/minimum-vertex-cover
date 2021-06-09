import csv
import gc
import jgrapht
import networkx as nx
import matplotlib.pyplot as plt
import os

from datetime import datetime
from time import process_time
from os.path import abspath, dirname


DIMACS_GRAPH = 1
SNAP_GRAPH = 2
CS6140_GRAPH = 3
BHOSLIB_GRAPH = 4


def parse_file(data_file, graph_format):
    adj_list = []
    with open(data_file) as f:
        if graph_format in (DIMACS_GRAPH, BHOSLIB_GRAPH):
            lines = f.readlines()
            for line in lines:
                keys = line.split()
                if keys[0] == 'e':
                    adj_list.append((int(keys[1]), int(keys[2])))
        elif graph_format == SNAP_GRAPH:
            lines = f.readlines()
            for line in lines:
                keys = line.split()
                if keys[0] != '#':
                    adj_list.append((int(keys[0]), int(keys[1])))
        elif graph_format == CS6140_GRAPH:
            num_nodes, num_edges, weighted = map(int, f.readline().split())
            for i in range(num_nodes):
                adj_list.append(map(int, f.readline().split()))
        return adj_list


def create_graph_from_file(data_file, graph_format=CS6140_GRAPH):
    adj_list = parse_file(data_file, graph_format)
    G = nx.Graph()
    if graph_format in (DIMACS_GRAPH, SNAP_GRAPH, BHOSLIB_GRAPH):
        for a, b in adj_list:
            G.add_edge(a, b)
    elif graph_format == CS6140_GRAPH:
        for i in range(len(adj_list)):
            for j in adj_list[i]:
                G.add_edge(i + 1, j)
    return G


def plot_graph(graph):
    pos = nx.circular_layout(graph)
    nx.draw(graph, pos, with_labels=True)
    labels = nx.get_edge_attributes(graph, 'weight')
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=labels)
    plt.show()


def nx_to_jgraph(graph):
    g = jgrapht.create_graph(directed=False, weighted=True,
                             allowing_self_loops=False, allowing_multiple_edges=False)
    g.add_vertices_from(list(graph.nodes))
    g.add_edges_from(list(graph.edges))
    return g


def run(methods, graph, is_jgrapht=False):
    for func, msg in methods:
        gc.collect()
        start = process_time()
        mvc = func(graph)
        end = process_time()
        if is_jgrapht:
            print(f'{msg} vertex cover: {int(mvc[0])}, execution time {end-start:0.5f}s')
        else:
            print(f'{msg} vertex cover: {len(mvc)}, execution time {end-start:0.5f}s')


def run_tests(own_methods, jgraph_methods, graph_format=CS6140_GRAPH, write_csv=False):
    BASE_DIR = dirname(abspath(__file__))
    src = format = ''
    csv_rows = []
    
    if graph_format == DIMACS_GRAPH:
        src = BASE_DIR + '/data/dimacs/'
        format = 'DIMACS'
    elif graph_format == BHOSLIB_GRAPH:
        src = BASE_DIR + '/data/bhoslib/'
        format = 'BHOSLIB'
    elif graph_format == SNAP_GRAPH:
        src = BASE_DIR + '/data/snap/'
        format = 'SNAP'
    elif graph_format == CS6140_GRAPH:
        src = BASE_DIR + '/data/cs6140/'
        format = 'CS6140'

    with os.scandir(src) as entries:
        for entry in entries:
            if entry.is_file():
                print(f'Processing file {entry.name}')
                print('-----')
                # build graph
                g = create_graph_from_file(src + entry.name, graph_format)
                # graph info
                num_nodes = g.number_of_nodes()
                num_edges = g.number_of_edges()
                print(f'No of nodes: {num_nodes}')
                print(f'No of edges: {num_edges}')
                print('-----')
                if own_methods:
                    for func, msg in own_methods:
                        gc.collect()
                        start = process_time()
                        mvc = func(g)
                        end = process_time()
                        mvc_size = len(mvc)
                        mvc_exec_time = end-start
                        print(f'{msg} vertex cover: {mvc_size}, execution time {mvc_exec_time:0.5f}s')
                        if write_csv:
                            csv_rows.append([format, entry.name, num_nodes, num_edges, msg, mvc_size, mvc_exec_time])
                print('-----')
                if jgraph_methods:
                    # build jgraph
                    jg = nx_to_jgraph(g)
                    # run
                    for func, msg in jgraph_methods:
                        gc.collect()
                        start = process_time()
                        mvc = func(jg)
                        end = process_time()
                        mvc_size = int(mvc[0])
                        mvc_exec_time = end-start
                        print(f'{msg} vertex cover: {mvc_size}, execution time {mvc_exec_time:0.5f}s')
                        if write_csv:
                            csv_rows.append([format, entry.name, num_nodes, num_edges, msg, mvc_size, mvc_exec_time])
                    print('-----')
    if write_csv:
        now = datetime.now().strftime("%Y%m%d%H%M%S")
        dest = f'{BASE_DIR}/output/result_{now}.csv'
        with open(dest, mode='w') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(['format', 'file', 'num_nodes', 'num_edges', 'method', 'mvc', 'exec_time'])
            csv_writer.writerows(csv_rows)
