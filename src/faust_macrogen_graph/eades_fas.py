"""
    Implementation of Eades et. al. (1993) minimal feedback arc set:
        see: 
            -   Eades, Peter / Lin, Xuemin / Smyth, W. F., "A Fast and Effective Heuristic for the Feedback Arc Set Problem," 
                in: Information Processing Letters (1993), Vol. 47(6), pp. 319-323.
            -   https://pdfs.semanticscholar.org/c7ed/d9acce96ca357876540e19664eb9d976637f.pdf
            
    By changing the parameter "deltamaximum" to False, you get the mininum delta-score node after the removal of sinks and sources
    as suggested by Tintelnot et. al. (2018):
        see:
            -   Tintelnot, Felix / Kikkawa, Ken / Mogstad, Magne / Dhyne, Emmanuel, "Trade and Domestic Production Networks",
                Cambridge 2018, p. 30f., Appendix E.
            -   http://felix-tintelnot.wdfiles.com/local--files/research/TKMD_draft.pdf
            -   whole Appendix: https://www.nber.org/data-appendix/w25120/w25120.appendix.pdf
"""

import networkx as nx
import matplotlib.pyplot as plt
from collections import deque

##############
# Helper functions
#############

def degrees(G):
    """Collects the in- and out-degrees of all nodes of a DiGraph in a dictionary.
    
    Args:
        G (DiGraph): A DiGraph-Object of networkx.
    Example:
        >>> print(degrees(G))
        {'A': [1, 2], 'B': [3, 2], 'C': [3, 1], 'D': [1, 2]}
    Returns:
        Dictionary of nodes with the in- and out-degrees of the nodes as values stored in a list.
    """
    degrees = {}
    for node in G.nodes():
        degrees[node] = [G.in_degree(node), G.out_degree(node)]
    return degrees

def deltadegrees(G, deltamaximum=True):
    """Collects the DeltaDegree of every node of a DiGraph in a dictionary.
        The DeltaDegree as in Eades paper "δ(u)" is computed by subtracting the in-degree from the out-degree of a node (DeltaMaximum).
        The DeltaDegree as in Tintelnots paper "δ(u)" is computed by subtracting the out-degree from the in-degree of a node (DeltaMinimum).
        
    Args:
        G (DiGraph): A DiGraph-Object of networkx.
        deltamaximum (bool): If True, the deltamaximum is computed, else the deltaminimum.
    Example:
        >>> print(deltadegrees(G)
        {'A': -1, 'B': 1, ''C': 2, 'D': -1})
    Returns:
        Dictionary of nodes with the DeltaDegree of each node as value.
    """
    delta_degrees = {}
    for node in G.nodes():
        if deltamaximum:
            delta_degrees[node] = G.out_degree[node] - G.in_degree[node]
        else:
            delta_degrees[node] = G.in_degree[node] - G.out_degree[node] 
    return delta_degrees


def gen_vertex2D(n_nodes, graph_nodes, degrees, delta_degrees):
    """Generate a two-dimensional array (= list), called vertex2Dlist, where the sources are inside the first nested list and the 
        sinkes are in the last nested list while the other nodes are sorted based on their DeltaDegree in one of the other lists.
        A node with a low DeltaDegree will be sorted nearby the beginning of the array and a node with a high DeltaDegree will be
        sorted nearby the end of the array (see the "bucket"-graphic in: Tintelnot (2018), Appendix E, p. 29).
    
    Args:
        n_nodes (int): Number of nodes of a DiGraph.
        graph_nodes (NodeView): A NodeView of all nodes of a DiGraph.
        degrees (dict): A Dictionary of all in- and out-degrees of every node of a DiGraph.
        delta_degrees (dict): A Dictionary of the DeltaDegree of every node of a DiGraph.
    Example:
        >>> print(gen_vertex2D(G.number_of_nodes(), G.nodes(), degrees(G), deltadegrees(G))
        [['A'], [], [], ['B'], ['C'], ['D'], [], [], ['E']]
    Returns:
        Vertex2Dlist (two-dimensional array) with the nodes sorted by sources to sinks while the the non-sink and non-sources nodes 
        are sorted by their DeltaDegree.
    """
    #generate an empty two-dimensional array by the formula 2n-1 in Tintelnots paper (see: Tintelnot (2018), Appendix E, p. 28)
    vertex2Dlist = [[] for node in range((2 * n_nodes) - 1)]
    
    #if the DiGraph only consists of one node, the node will be treated as source
    if len(graph_nodes) == 1:
        for node in graph_nodes:
            vertex2Dlist[0].append(node)
    else:
        for node in graph_nodes:
            #check if node is a source
            if degrees[node][0] == 0 and degrees[node][1] > 0: 
                vertex2Dlist[0].append(node)
            #check if node is a sink
            elif degrees[node][1] == 0 and degrees[node][0] > 0:
                vertex2Dlist[-1].append(node)
            #if node is neither a source nor a sink, add the nodes to the sequence:
            # - nodes with a lower deltadegree more to the "left" (nearby to source)
            # - nodes with a higher deltadegree more to the "right" (nearby to sink)
            else:
                delta_degree = delta_degrees[node]
                vertex2Dlist[(n_nodes-1) + delta_degree].append(node)
    return vertex2Dlist


#############
# EADES GREEDY ALGORITHM
#############

def eades_GR(vertex2Dlist, G, deltamaximum=True):
    """Implementation of Eades greedy algorithm "GR" which computes a "good" Vertex Sequence (type = deque) which induces a feedback arc set
        consisting of all the leftward edges (see: Eades (1993), p. 320)
    
        Args:
            vertex2Dlist (list): two-dimensional array (= lists) with sorted nodes based on their DeltaDegree or their sink or source feature.
            G (DiGraph): A Directed Graph (networkx DiGraph) with cycles.
            deltamaximum (bool): If True, the deltamaximum is computed, else the deltaminimum.
        Example:
            >>> eades_GR(vertex2Dlist, G)
            deque(['A', 'B', 'D', 'C', 'E'])
        Returns:
            Sorted, "good" Vertex Sequence (type = deque) as described by Eades (see: Eades (1993), p. 320) which induces a feedback arc set 
            consisting of all the leftward edges.
    """
    
    G = G.copy()
    s1 = deque() #left part of the Vertex Sequence
    s2 = deque() #right part of the Vertex Sequence
    n_nodes = G.number_of_nodes() #static number of Graph nodes
    removed_nodes = []
    
    while len(removed_nodes) < n_nodes:
        
        #access the end of the vertex2Dlist where the sinks are stored and added to the right part of the vertexsequence
        try:
            while vertex2Dlist[-1]:
                if vertex2Dlist[-1]:
                    try:
                        sink = vertex2Dlist[-1][0]
                        s2.appendleft(sink)
                        G.remove_node(sink)
                        removed_nodes.append(sink)
                        vertex2Dlist[-1].pop(0)
                        vertex2Dlist = gen_vertex2D(n_nodes, G.nodes(), degrees(G), deltadegrees(G, deltamaximum))
                    except KeyError:
                        break
        except IndexError:
            pass

        #access the beginning of the vertex2Dlist where the sources are stored and added to the left part of the vertexsequence
        try:  
            while vertex2Dlist[0]:
                if vertex2Dlist[0]:
                    try:
                        source = vertex2Dlist[0][0] 
                        s1.append(source)
                        G.remove_node(source)
                        removed_nodes.append(source)
                        vertex2Dlist[0].pop(0)
                        vertex2Dlist = gen_vertex2D(n_nodes, G.nodes(), degrees(G), deltadegrees(G, deltamaximum))
                    except KeyError:
                        break
        except IndexError:
            pass
        
        #choose a vertex for which the delta_degree is maximum (minimum)
        if len(removed_nodes) < n_nodes:
            delta_degrees = deltadegrees(G, deltamaximum)
            
            if deltamaximum:
                delta_degree_node = max(delta_degrees, key=delta_degrees.get)
            else:
                delta_degree_node = min(delta_degrees, key=delta_degrees.get)
            s1.append(delta_degree_node)
            G.remove_node(delta_degree_node)
            removed_nodes.append(delta_degree_node)
          
        vertex2Dlist = gen_vertex2D(n_nodes, G.nodes(), degrees(G), deltadegrees(G, deltamaximum))

  
    return s1+s2

########
# Building graph from vertex2Dlist
########

def gen_FAS(vertexsequence, G):
    """Computing a Feedback Arc Set (FAS) out of a "good" Vertex Sequence using a modified Depth-First-Search (DFS). For DFS of Connected Compontens see: 
        Mann, Edd, "Depth-First Search and Breadth-First Search in Python", https://eddmann.com/posts/depth-first-search-and-breadth-first-search-in-python/
        (last accessed on 12th February 2019)).
    
        Args:
            vertexsequence (deque): "Good" Vertex Sequence as described by Eades (see: Eades (1993), p. 320).
            G (DiGraph): A Directed Graph (networkx DiGraph) with cycles.
        Example:
            >>> gen_FAS(vertexsequence, G.copy())
            {('D', 'A', 1.0), ('Z', 'W', 1.0), ('J', 'H', 1.0)}
        Returns:
            Set of edges which represents the Feedback Arc Set (FAS).
    """
    
    #label each node from the left to the right with their position inside the Vertex Sequence
    node_positions = {node: idx for idx, node in enumerate(vertexsequence)}
    
    #set of starting nodes for every component of G
    startingnodes = set((component.pop() for component in nx.connected_components(G.to_undirected())))
    visited = set([vertexsequence[0]])
    
    #feedback arc set
    fas = []
  
    for startnode in startingnodes:
        stack = deque([startnode])
        while stack:
            current_node = stack.pop()
            
            #reversed in-edges
            in_edges = [(x,y) for y,x in G.in_edges(current_node)]
            edges = list(G.out_edges(current_node)) + in_edges
            for (x, y) in edges:
                #check if edge is a backward edge based on the node_positions
                if node_positions[y] < node_positions[current_node]:
                    try:
                        if (current_node, y, G[current_node][y]["weight"]) not in fas:
                            fas.append((current_node, y, G[current_node][y]["weight"]))
                    except KeyError:
                        pass
                #add the visited node to the visited-set
                if y not in visited:
                    stack.append(y)
                    visited.add(y)
    
    return set(fas)


def eades_FAS(G, deltamaximum):
    """
    Args:
        G (DiGraph): A DiGraph-Object of networkx with cycles.
        deltamaximum (bool): If True, the deltamaximum is computed, else the deltaminimum.
    Example:
        >>> fas = eades_FAS(G, True)
        {('D', 'A', 1.0), ('Z', 'W', 1.0), ('J', 'H', 1.0)}
    Returns:
        Set of edges which can be removed from a graph to make it acyclic (Feedback Arc Set (FAS)).
    """
    n_nodes = G.number_of_nodes()
    
    if n_nodes != 0:
        graph_nodes = G.nodes()
        node_degrees =  degrees(G)
        delta_degrees = deltadegrees(G, deltamaximum)
        vertex2Dlist = gen_vertex2D(n_nodes, graph_nodes, node_degrees, delta_degrees)
        vertexsequence = eades_GR(vertex2Dlist, G, deltamaximum)
        fas = gen_FAS(vertexsequence, G.copy())
    
    return fas


#%%
#####
# Creating Graph
#####
    
if __name__ == '__main__':

    G = nx.DiGraph()
    #first component of G
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
    G.add_edge("K", "L", weight=1.0)
    
    #second component of G
    G.add_edge("W", "X", weight=1.0)
    G.add_edge("X", "Y", weight=1.0)
    G.add_edge("Y", "Z", weight=1.0)
    G.add_edge("Z", "W", weight=1.0)

    pos = nx.shell_layout(G)
    nx.draw_networkx_nodes(G, pos)
    nx.draw_networkx_labels(G, pos)
    nx.draw_networkx_edges(G, pos)
    plt.show()
    

    if nx.is_directed_acyclic_graph(G) == False:
        print("The graph contains cycles.")
    else:
       print("The graph contains no cycles.")
    fas = eades_FAS(G, True)
    print("\nThese are the edges from the Feedback Arc Set, which will be removed from the graph: " + str(fas) + "\n")
    G.remove_edges_from(fas)
    pos = nx.shell_layout(G)
    nx.draw_networkx_nodes(G, pos)
    nx.draw_networkx_labels(G, pos)
    nx.draw_networkx_edges(G, pos)
    plt.show()
    if nx.is_directed_acyclic_graph(G) == False:
        print("The graph still contains cycles")
    else:
       print("The graph doesn't contain any cycles. It is now acyclic.")
    
    
    
    
    
    
    
