#%%
#TODO: docstrings for all überprüfen
#TODO: ^
#TODO: |
import networkx as nx
from collections import Counter
import re
from datetime import datetime, timedelta
from faust_macrogen_graph import approachesutils


#####
# functions for the relation elements
#####

def add_egdes_from_node_list(G, nodelist):
    """Add an edge from every node of a list of nodes to the next node in the list with the source as edge attribute.
    
    Args:
        G (DiGraph): DiGraph-Object of networkx.
        nodelist (list): list with 2-tuples, where the first item is a list of sources and the second item is a tuple of nodes in a given order.
    Returns:
        Enhanced input-graph with the nodes and edges of the nodelist and the source as edge attribute.
    """
    #only first source is taken if more than one source exists
    source_name = nodelist[0][0]
    node_tuple = nodelist[1]
    nG = G
    for index, node in enumerate(node_tuple):
        current_node = node
        next_node = node_tuple[(index + 1) % len(node_tuple)]
        if next_node == node_tuple[0]:
            break
        
        #no loop
        if current_node == next_node:
            pass
        else:
            nG.add_edge(current_node, next_node, weight=1.0, source=source_name)
    return nG


#####
# functions for the date elements
####
    
#TODO: docstring
def add_edges_from_dates_list(G, dates_list):
    """
    """
    nG = G
    for t in dates_list:
        
        manuscript = t[0]
        date_item = t[1][0]
        source_name = t[1][1]

        #in case of special case of Paulus approaches where @when attribute gets a higher weight
        if len(t[1]) == 3:
            nG.add_edge(str(date_item), manuscript, weight=t[1][2], source=source_name)
        elif len(t[1]) == 4:
            nG.add_edge(str(date_item), manuscript, weight=1.0, source=source_name)
            nG.add_edge(manuscript, str(t[1][3]), weight=1.0, source=source_name)
        else:
            nG.add_edge(str(date_item), manuscript, weight=1.0, source=source_name)
    return nG

def graph_from_dates(date_items, approach, special_researchers, factor=4):
    """Generates a graph out of date_items by connecting nodes through edges based on one of four different systems (= approaches).
    
    Args:
        date_items (list): 3-tuple, where the first item is a list of sources, the second item a tuple of nodes in a given order 
                            and the third items is a dictionary with the keys "notBefore", "notAfter" and "when".
        approach (string): One of the following four approaches: wissenbach, vitt, paulus-1, paulus-2.
        special_resarchers (dict): Dictionary with sources (string) as keys and their publication year (int) as values.
        factor (int): Integer which will be divided with the period between two dates.
    Returns:
        A Directed Graph Object of networkx with edges and nodes based on one of the four approaches.
    """
    G = nx.DiGraph()
    
    if approach == "wissenbach":
        wissenbach_d = approachesutils.dates_wissenbach(date_items, special_researchers)
        wissenbach_ds = [(k, wissenbach_d[k]) for k in sorted(wissenbach_d, key=wissenbach_d.get, reverse=False)]
        G = add_edges_from_dates_list(G, wissenbach_ds)
    elif approach == "vitt":
        vitt_d = approachesutils.dates_vitt(date_items)
        vitt_ds = [(k, vitt_d[k]) for k in sorted(vitt_d, key=vitt_d.get, reverse=False)]
        G = add_edges_from_dates_list(G, vitt_ds)
    elif approach == "paulus-1":
        paulus1_d = approachesutils.dates_paulus(date_items, special_researchers)
        paulus1_ds = [(k, paulus1_d[k]) for k in sorted(paulus1_d, key=paulus1_d.get, reverse=False)]
        G = add_edges_from_dates_list(G, paulus1_ds)
    elif approach == "paulus-2":
        paulus2_d = approachesutils.dates_paulus(date_items, special_researchers, False)
        paulus2_ds = [(k, paulus2_d[k]) for k in sorted(paulus2_d, key=paulus2_d.get, reverse=False)]
        G = add_edges_from_dates_list(G, paulus2_ds)
    elif approach == "shorter_period":
        sp_d = approachesutils.dates_shorter_period(date_items, factor)
        sp_ds = [(k, sp_d[k]) for k in sorted(sp_d, key=sp_d.get, reverse=False)]
        G = add_edges_from_dates_list(G, sp_ds)
    elif approach == "longer_period":
        lp_d = approachesutils.dates_longer_period(date_items, factor)
        lp_ds = [(k, lp_d[k]) for k in sorted(lp_d, key=lp_d.get, reverse=False)]
        G = add_edges_from_dates_list(G, lp_ds)

    return G