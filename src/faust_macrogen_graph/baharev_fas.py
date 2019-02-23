import networkx as nx
import matplotlib.pyplot as plt
from collections import deque
import itertools



def to_cycle(simple_path_nodes):
    seq = rotate_min_to_first_pos(simple_path_nodes)
    a, b = itertools.tee(seq)
    next(b, None)
    return tuple( izip_longest(a, b, fillvalue=seq[0]) )

def get_all_cycles(G, cutoff=500):
    # Try to enumerate cutoff+1 simple cycles
    cycles = list(itertools.islice(nx.simple_cycles(G), cutoff+1))
    # If that succeeds, we give up
    if len(cycles) > cutoff:
        print('More than', cutoff, 'simple cycles, giving up...')
        return False, None
    # Otherwise we have enumerated ALL cycles, we return the edges of each
    edges_per_cycle = [to_cycle(c) for c in cycles ]
    return True, edges_per_cycle



#TODO: get all cycles von baharev kopieren und einfacher anwenden auf baharev_fas
def edges_per_cycle(G):
    ...

#TODO: is 1 if edge j participates in cycle i and 0 otherwise
def calc_y(j, fas):
    """
    
    Returns:
        1 if edge j participates in cycle i and 0 otherwise.
    """
    
    ...
    
#TODO: calculate the matrix A called the cycle matrix
def calc_cyclematrix(G):
    ...
#%%
#####
# main baharev fas
#####

def baharev_FAS(G, fas):
    """
        Args:
            G (DiGraph): A Directed Graph (networkx DiGraph) with cycles and nonnegative edge weights.
    """
    m = list(G.edges())
    #w = weigths of the edges
    l = len(list(nx.simple_cycles(G)))
    
    for j in m:
        u = j[0]
        v = j[1]
        w = G[u][v]["weight"]
        
        y = calc_y(j, fas)
    
    
    fas = set()
    
    
    
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
    
    
#%%
    print(list(G.edges()))
    print(G["A"]["B"]["weight"])
    
    
    
#%%
    """
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
    """