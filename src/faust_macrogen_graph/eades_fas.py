import networkx as nx
import matplotlib.pyplot as plt
from collections import deque

##############
# Helper functions
#############

def degrees(G):
    """
    Args:
    
    Example:
        >>> print(degrees(G))
        {'A': [1, 2], 'B': [3, 2], 'C': [3, 1], 'D': [1, 2]}
    
    Returns:
        Dict of nodes with the in_degree and out_degree of the node as values stored in a list
    """
    degrees = {}
    for node in G.nodes():
        degrees[node] = [G.in_degree(node), G.out_degree(node)]
    return degrees

def deltadegrees(G):
    """
    
    Example:
        >>> print(deltadegrees(G)
        {'A': -1, 'B': 1, ''C': 2, 'D': -1})
    
    deltadegree = in-degree - out_degree
    """
    delta_scores = {}
    for node, in_degree in G.in_degree:
        delta_scores[node] = in_degree - G.out_degree[node]
    return delta_scores

#TODO: maybe rename because it isnt realy a vertexsequence
def gen_vertexsequence(n_nodes, graph_nodes, degrees, deltadegrees):
    """
    Args:
        n_nodes(int): number of nodes in a graph.
    Returns:
        Vertexsequence (multidimensional array) sorted by sources to sinks
        
    """
    vertexsequence = [[] for node in range((2 * n_nodes) - 1)] #empty [[], [], ...]
    
    if len(graph_nodes) == 1:
        for node in graph_nodes:
            vertexsequence[0].append(node)
    else:
    
        for node in graph_nodes:
            #check if node is a source
            if degrees[node][0] == 0 and degrees[node][1] > 0: 
                vertexsequence[0].append(node)
            #check if node is a sink
            elif degrees[node][1] == 0 and degrees[node][0] > 0:
                vertexsequence[-1].append(node)
            #if node is neither a source nor a sink, add the nodes to the sequence:
            # - nodes with a lower deltadegree more to the "left"
            # - nodes with a higher deltadegree more to the "right"
            else:
                deltavalue = deltadegrees[node]
                #adding G.number_of_nodes()-1 because of doubled size of the tmp_array in comparsion to the number of nodes
                try:
                    vertexsequence[(n_nodes-1) + deltavalue].append(node)
                except:
                    break

    return vertexsequence


#############
# EADES GREEDY ALGORITHM
#############

def eades_GR(vertexsequence, G, deltamaximum=True):
    """
        Args:
            vertexsequence ():
            G (DiGraph): A Directed Graph with cycles.
        Returns:
            Vertexsequence
    """
    
    G = G.copy()
    s1 = deque() #right
    s2 = deque() #left
    n_nodes = G.number_of_nodes() #fix number of Graph nodess
    removed_nodes = []
    
    while len(removed_nodes) < n_nodes:
        
        #access the end of the vertexsequence where the sinks are stored
        try:
            while vertexsequence[-1]:
                if vertexsequence[-1]:
                    try:
                        sink = vertexsequence[-1][0]
                        s2.appendleft(sink)
                        G.remove_node(sink)
                        removed_nodes.append(sink)
                        vertexsequence[-1].pop(0)
                        vertexsequence = gen_vertexsequence(n_nodes, G.nodes(), degrees(G), deltadegrees(G))
                    except KeyError:
                        break
        except IndexError:
            pass
                
        
        try:
        #access the beginning of the vertexsequence where the source are stored    
            while vertexsequence[0]:
                if vertexsequence[0]:
                    try:
                        source = vertexsequence[0][0] 
                        s1.append(source)
                        G.remove_node(source)
                        removed_nodes.append(source)
                        vertexsequence[0].pop(0)
                        vertexsequence = gen_vertexsequence(n_nodes, G.nodes(), degrees(G), deltadegrees(G))
                    except KeyError:
                        break
        except IndexError:
            pass
                
        if len(removed_nodes) < n_nodes:
            delta_degrees = deltadegrees(G)
            
            if deltamaximum:
                delta_degree_node = max(delta_degrees, key=delta_degrees.get)
            else:
                delta_degree_node = min(delta_degrees, key=delta_degrees.get)
            s1.append(delta_degree_node)
            G.remove_node(delta_degree_node)
            removed_nodes.append(delta_degree_node)
            
        vertexsequence = gen_vertexsequence(n_nodes, G.nodes(), degrees(G), deltadegrees(G))

  
    return s1+s2


#%%
########
# Building graph from vertexsequence
########

def graph_from_vertexsequence(s, G):
    order = {x: i for i, x in enumerate(s)} #{'A': 0, 'B': 1, 'D': 2, 'C': 3, 'E': 4}
    GG = G.to_undirected()
    
    #in case of more than one components of GG
    starting_points = [x.pop() for x in nx.connected_components(GG)] #[c, c]
    
    visited = set([s[0]]) #{A}
    #TODO: rename
    violator_set = []
    
    #TODO: rename s_0
    for s_0 in starting_points:
        #TODO: rename  q; maybe queue
        q = deque([s_0])
        while q:
            cur_node = q.pop()
            #reversed in edges --> why?
            in_edges = [(x,y) for y,x in G.in_edges(cur_node)] #[('C', 'D')]
            edges = list(G.out_edges(cur_node)) + in_edges #[('C', 'B'), ('C', 'D')]
            #TODO: change to tuple??
            for (y, x) in edges:
                #x = edge[1]
                #check if backward edge
                if order[x] < order[cur_node]: #o[x = "B", "D"] = 1, o["C"] = 3
                    try:
                        if (cur_node, x, G[cur_node][x]["weight"]) not in violator_set:
                            print("violator edge: {0}-{1}".format(cur_node, x))
                            violator_set.append((cur_node, x, G[cur_node][x]["weight"]))
                    except KeyError:
                        pass
                #add the visited node from current nodes to the visited-set
                if x not in visited:
                    q.append(x)
                    visited.add(x)
    violator_set = set(violator_set)

    
    return violator_set


def eades_FAS(G, deltamaximum):
    """
    
    Returns:
        list of edges which can be removed from a graph to make it acyclic
    """
    n_nodes = G.number_of_nodes()
    graph_nodes = G.nodes()
    node_degrees =  degrees(G)
    delta_degrees = deltadegrees(G)
    vertexsequence = gen_vertexsequence(n_nodes, graph_nodes, node_degrees, delta_degrees)
    s = eades_GR(vertexsequence, G, deltamaximum)
    fas = graph_from_vertexsequence(s, G.copy())
    
    return fas


#%%
#####
# Creating Graph
#####

G = nx.DiGraph()

G.add_edge("A", "B", weight=1.0)
G.add_edge("A", "F", weight=1.0)
G.add_edge("B", "I", weight=1.0)
G.add_edge("B", "J", weight=1.0)
G.add_edge("C", "B", weight=1.0)
G.add_edge("D", "A", weight=1.0)
G.add_edge("D", "C", weight=1.0)
G.add_edge("E", "G", weight=1.0)
G.add_edge("F", "C", weight=1.0)
G.add_edge("F", "D", weight=1.0)
G.add_edge("G", "C", weight=1.0)
G.add_edge("H", "B", weight=1.0)
G.add_edge("H", "G", weight=1.0)
G.add_edge("H", "L", weight=1.0)
G.add_edge("J", "H", weight=1.0)
G.add_edge("L", "E", weight=1.0)
G.add_edge("M", "L", weight=1.0)

nx.draw_networkx(G)
plt.show()
print(nx.is_directed_acyclic_graph(G))
"""
G = nx.DiGraph()
G.add_edge("A", "B", weight=1.0)
G.add_edge("B", "D", weight=1.0)
G.add_edge("D", "E", weight=1.0)
G.add_edge("C", "B", weight=1.0)
G.add_edge("D", "C", weight=1.0)
nx.draw_networkx(G)
plt.show()
print(nx.is_directed_acyclic_graph(G))
"""

