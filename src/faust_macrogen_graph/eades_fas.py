#%%
import networkx as nx
import matplotlib.pyplot as plt
import operator
from collections import deque

def deltadegree(graph):
    """deltadegree = in-degree - out_degree
    """
    delta_scores = {}
    for node, in_degree in graph.in_degree:
        delta_scores[node] = in_degree - graph.out_degree[node]
    return delta_scores

#TODO: ändern
def node_degrees2(graph):
    """
    
    Returns:
        Dict of nodes with the in_degree and out_degree of the node as values
    """
    degrees = {}
    for node, in_degree in graph.in_degree():
        degrees[node] = [in_degree, graph.out_degree[node]]
    return degrees

#TODO: bearbeiten, Variablen umbenennen
# = gen_buckets
def vertexsequence(graph):
    """
    Returns:
        #Vertexsequence (list) sort by sources to sinks
        
    """
    #vs = []
    tmp_array = [[] for node in range((2 * graph.number_of_nodes()) - 1)] #empty [[], [], ...]
    ndegrees = node_degrees2(graph)
    delta_scores = deltadegree(graph)

    for node in graph.nodes():
        #check if node is a source
        if ndegrees[node][0] == 0 and ndegrees[node][1] > 0: 
            tmp_array[0].append(node)
        #check if node is a sink
        elif ndegrees[node][1] == 0 and ndegrees[node][0] > 0:
            tmp_array[-1].append(node)
        else:
            deltascore = delta_scores[node]
            #adding G.number_of_nodes()-1 because of doubled size of the tmp_array in comparsion to the number of nodes
            tmp_array[(graph.number_of_nodes()-1) + deltascore].append(node)
    #multidimensional tmp_array to onedimensional list
    #for l in tmp_array:
    #    if l:
    #        vs.append(l)
    return tmp_array


G = nx.DiGraph()
G.add_edge("A", "B")
# G.add_edge("B", "A", weight=1.0)
G.add_edge("B", "D")
G.add_edge("D", "E")
G.add_edge("C", "B")
G.add_edge("D", "C")
print(nx.is_directed_acyclic_graph(G))
nx.draw_networkx(G)
plt.show()
print(vertexsequence(G))

#%%
def update_n(n_nodes, vs, removed_nodes, delta_scores, node_degrees, lowest, neighbours, parity=1, node=None):
    parity = -1 if parity < 0 else 1 # normalise parity
    mid = n_nodes - 1
        
    for node, _ in neighbours:
        node = node if parity >= 0 else _
        
        if node in vs[0] or node in vs[-1] or node in removed_nodes: continue
    
        ind = mid + delta_scores[node]
        
        x = vs[ind].remove(node)
        
        delta_scores[node] += parity
        _deg = 1 if parity >= 0 else 0
        node_degrees[node][_deg] -= 1
        
        # Check if node becomes a sink/source or if it moves to an adjecent bucket
        if node_degrees[node][_deg] > 0 and node_degrees[node][not _deg] > 0:
            vs[delta_scores[node] + mid].append(node)
        else:
            vs[-1 if parity > 0 else 0].append(node)
        
        # Track the min in O(1) amortised
        # (if the bucket with the min becomes null it means the min has been moved up by one)
        if not vs[int(lowest) + mid] or delta_scores[node] < int(lowest):
            if node_degrees[node][_deg] > 0 and node_degrees[node][not _deg] > 0:
                lowest = delta_scores[node]
    
    if not vs[int(lowest)+mid] and len(removed_nodes) < n_nodes:
        lowest = min([delta_scores[x] for x in delta_scores if x not in removed_nodes])
        
    return n_nodes, vs, neighbours, removed_nodes, delta_scores, node_degrees
        
    

def eades_fas(graph):
    
    delta_scores = deltadegree(graph)
    
    
    vs = vertexsequence(graph)
    
    
    node_degrees = node_degrees2(graph)
    #TODO: remove
    #vs = buckets
    n_nodes = graph.number_of_nodes()
    s1 = deque()
    s2 = deque()
    removed_nodes = set()
    
    while (len(removed_nodes) < n_nodes):
        
        while(vs[-1]):
            if vs[-1]:
                sink = vs[-1][0]
                s2.appendleft(sink)
                
                #update_buckets
                #self.update_buckets(self.buckets[ind].pop(0))
                current_node = vs[-1].pop(0)
                lowest = min(float(delta_scores[current_node]), float("inf"))

                
                
                n_nodes, vs, removed_nodes, delta_scores, node_degrees, lowest = update_n(n_nodes, vs, removed_nodes, 
                                                                                              delta_scores, node_degrees, lowest,
                                                                                              list(graph.in_edges(current_node)), 1, current_node)
                n_nodes, vs, removed_nodes, delta_scores, node_degrees, lowest = update_n(n_nodes, vs, removed_nodes, 
                                                                                              delta_scores, node_degrees, lowest,
                                                                                              list(graph.out_edges(current_node)), -1, current_node)
                #self.update_neighbours(list(self.G.in_edges(node)), 1, node) # update buckets for ingoing nodes to node
                #self.update_neighbours(list(self.G.out_edges(node)), -1, node) # update buckets for outgoing nodes to node

            #del delta_scores[sink]
            #vs[-1].pop(0)
            #n_nodes = n_nodes - 1
            
        while(vs[0]):
            source = vs[0][0]
            s1.append(source)
            current_node = vs[0].pop(0)
            lowest = min(float(delta_scores[current_node]), float("inf"))
            n_nodes, vs, removed_nodes, delta_scores, node_degrees = update_n(n_nodes, vs, removed_nodes, 
                                                                                              delta_scores, node_degrees, 
                                                                                              list(graph.in_edges(current_node)), 1, current_node)
            n_nodes, vs, removed_nodes, delta_scores, node_degrees = update_n(n_nodes, vs, removed_nodes, 
                                                                                              delta_scores, node_degrees, 
                                                                                              list(graph.out_edges(current_node)), -1, current_node)
            #del delta_scores[source]
            #vs[0].pop(0)
            #n_nodes = n_nodes - 1
            
        if len(removed_nodes) < n_nodes:
            
            lowest = min(float(delta_scores[current_node]), float("inf"))
            index = (n_nodes-1) + int(lowest)
            
            if index < 0 or index >= len(vs) - 1:
                s2.appendleft(vs[index][0])
            else:
                s1.append(vs[index][0])
            
            current_node = vs[index].pop(0)
            
            n_nodes, vs, removed_nodes, delta_scores, node_degrees, lowest = update_n(n_nodes, vs, removed_nodes, 
                                                                                              delta_scores, node_degrees, lowest,
                                                                                              list(graph.in_edges(current_node)), 1, current_node)
            
            """
            maximum_node = search_maximum_degree(delta_scores)
            s1.append(maximum_node)
            del delta_scores[maximum_node]
            for i, l in enumerate(vs):
                for idx, node in enumerate(l):
                    if node == maximum_node:
                        vs[i].pop(idx)
                        break

            
            n_nodes = n_nodes - 1
            """
    
    s1 = deque(s1)
    s = s1.extend(s2)
    return s

G = nx.DiGraph()
G.add_edge("A", "B")
# G.add_edge("B", "A", weight=1.0)
G.add_edge("B", "D")
G.add_edge("D", "E")
G.add_edge("C", "B")
G.add_edge("D", "C")
print(nx.is_directed_acyclic_graph(G))
nx.draw_networkx(G)
plt.show()
print(vertexsequence(G))

#%%
def search_maximum_degree(delta_scores):
    return max(delta_scores.items(), key=operator.itemgetter(1))[0]

def edgelist_from_vertexsequence(vertexsequence, edges):
    """
        Args: 
            vertexsequence
            edges (list with tupels): List with edge-tupels from a graph.
            
        Returns:
            
    """
    edgelist = []
    #removed_edges = []
    vs = vertexsequence.copy()
    for idx, node in enumerate(vs):
        n = idx + 1
        while(n < len(vs)):
            nxt_node = vs[(n) % len(vs)]
            t = (node, nxt_node)
            rt = t[::-1] #backward edge
            #no backward edges
            if t in edges and rt not in edgelist:
                edgelist.append(t)
                
            n += 1
            
    return edgelist
"""
def removed_edges(edgelist, edges):
    removed_edges = []
    for edge in edges:
        if edge not in edgelist:
            removed_edges.append(edge)
            
    return removed_edges
#, removed_edges
"""

def ev(vs, graph, uG):
    
    vs = deque(vs)
    #TODO: weg, ändern oder löschen
    order = {x: i for i, x in enumerate(vs)}
    #uG = graph.to_undirected()
    starting_nodes = [node.pop() for node in nx.connected_components(uG)] #in case of more than one component of the graph
    visited = set([vs[0]])
    removed_edges = []
    
    for node in starting_nodes:
        q = deque([node])
        while q:
            current_node = q.pop()
            #TODO: change ...
            #had to revert the edges for ...
            node_in_edges = [(u, v) for v, u in graph.in_edges(current_node)]
            node_all_edges = list(graph.out_edges(current_node)) + node_in_edges
            
            for _, u in node_all_edges:
                if order[u] < order[current_node]:
                    #t = (current_node, u)
                    try:
                        if (current_node, u) not in removed_edges:
                            #TODO: ändern, löschen
                            print("böse kante")
                            print((current_node, u))
                            removed_edges.append((current_node, u))
                    except KeyError:
                        pass
                if u not in visited:
                    q.append(u)
                    visited.add(u)
    removed_edges = set(removed_edges)           
    for u, v in removed_edges:
        graph.remove_edge(u, v)
        
    return graph
            
#%%
G=nx.gn_graph(8)
G.add_edge(7, 1)
G.add_edge(7, 3)
G.add_edge(7, 5)
G.add_edge(1, 7)
print(nx.is_directed_acyclic_graph(G))
nx.draw_networkx(G)
plt.show()
"""
GG = G.to_undirected()
nx.draw_networkx(GG)
plt.show()
starting_points = [print(x) for x in nx.connected_components(GG)]
print(nx.connected_components(GG))
"""
#%%
G = nx.DiGraph()
G.add_edge("A", "B")
# G.add_edge("B", "A", weight=1.0)
G.add_edge("B", "D")
G.add_edge("D", "E")
G.add_edge("C", "B")
G.add_edge("D", "C")
print(nx.is_directed_acyclic_graph(G))
nx.draw_networkx(G)
plt.show()
#%%
print(eades_fas(G.copy()))
#%%
vs = eades_fas(G.copy())
ng = ev(vs, G.copy(), G.copy().to_undirected())
print(nx.is_directed_acyclic_graph(ng))
nx.draw_networkx(ng)
plt.show()
#%%
vs = eades_fas(G)
print(vertexsequence(vs))
#%%
edges = G.edges()
print(edges)
edgelist = edgelist_from_vertexsequence(vs, list(edges))
print(edgelist)
print("removed edges")
print(removed_edges(edgelist, edges))
#%%
G2 = nx.DiGraph()
G2.add_edges_from(edgelist)
print(nx.is_directed_acyclic_graph(G2))
nx.draw_networkx(G2)
plt.show()

#TODO: rename vertex sequence function
#TODO: edgelist_from_vertexsequence doesnt' work 
#%%

print(eades_fas(G.copy()))
nx.draw_networkx(G)
plt.show()
