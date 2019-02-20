import networkx as nx
import matplotlib.pyplot as plt
from collections import deque

def baharev_FAS(G):
    """
        Args:
            G (DiGraph): A Directed Graph (networkx DiGraph) with cycles and nonnegative edge weights.
    """
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