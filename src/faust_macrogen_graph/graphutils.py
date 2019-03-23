import networkx as nx
from faust_macrogen_graph import approachesutils, parserutils
from pathlib import Path

#####
# functions for the relation elements
#####

def add_egdes_from_node_list(G, nodelist, temppre=True):
    """Add an edge from every node of a list of nodes to the next node in the list with the source as edge attribute.
    
    Args:
        G (DiGraph): DiGraph-Object of networkx.
        nodelist (list): List with 2-tuples, where the first item is a list of sources and the second item is a tuple of nodes in a given order.
        temppre (bool): If True, the edges get the weight=1.0, if False, they get the weight=5.0.
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
            if temppre:
                nG.add_edge(current_node, next_node, weight=1.0, source=source_name)
            else:
                #tempsyn elements get another weight
                nG.add_edge(current_node, next_node, weight=5.0, source=source_name)
    return nG


#####
# functions for the date elements
####
    
def add_edges_from_dates_list(G, dates_list):
    """Generate a directed Graph with manuscript and dates as nodes based on a list of dates and manuscripts.    
    
    Args:
        G (DiGraph): DiGraph-Object of networkx.
        dates_list (list, tuple): List or tuple of manuscripts sorted by dates with the structure: 
                                    [manuscript, (date, source, "weight", "end_date")]. The elements 
                                    in quotation marks are optional.
    Returns:
        DiGraph-Object of networkx with manuscript and dates as nodes and sources as edge-attributes.
    """
    nG = G
    for t in dates_list:
        
        manuscript = t[0]
        date_item = t[1][0]
        source_name = t[1][1]

        #when an approach gives a different weight to the @when-attribute
        if len(t[1]) == 3:
            nG.add_edge(str(date_item), manuscript, weight=t[1][2], source=source_name)
        #when an approach has two date-nodes
        elif len(t[1]) == 4:
            nG.add_edge(str(date_item), manuscript, weight=1.0, source=source_name)
            nG.add_edge(manuscript, str(t[1][3]), weight=1.0, source=source_name)
        else:
            nG.add_edge(str(date_item), manuscript, weight=1.0, source=source_name)
    return nG

def graph_from_dates(date_items, approach, special_researchers, factor=4):
    """Generates a graph out of date_items by connecting nodes through edges based on one of six different systems (= approaches).
    
    Args:
        date_items (list): 3-tuple, where the first item is a list of sources, the second item a tuple of nodes in a given order 
                            and the third items is a dictionary with the keys "notBefore", "notAfter" and "when".
        approach (string): One of the following six approaches: wissenbach, vitt, paulus-1, paulus-2, shorter_period, longer_period.
        special_resarchers (dict): Dictionary with sources (string) as keys and their publication year (int) as values.
        factor (int): Integer which will be divided with the period between two dates or added/subtracted from a date.
    Returns:
        A Directed Graph Object of networkx with edges and nodes based on one of the six approaches.
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

#####
# functions for whole graph
#####

def remove_edges_by_source(G, source):
    """Removes edges of Directed Graph on the basis of the input source.
    
    Args:
        G (DiGraph): DiGraph-Object of networkx.
        source (string): Source name as string.
    Returns:
        G without the edges with the input source attribute.
    """
    
    nG = G.copy()
    removed_edges = []
    sourcenames = nx.get_edge_attributes(nG, "source")
    for edge in nG.edges():
        try:
            if sourcenames[(edge[0], edge[1])] == source:
                removed_edges.append((edge[0], edge[1]))
        except:
            pass
        
    for edge in removed_edges:
         nG.remove_edge(edge[0], edge[1])
        
    return nG

def readding_edges_by_source(G, aG, fas, critical_sources, readded_edgelist=False):
    """Add egdes from critical sources of a FAS to an acyclic graph step by step to keep his acyclic nature.    
    
        Args:
            G (DiGraph): Cyclic DiGraph-Object of networkx.
            aG (DiGraph): Acyclic DiGraph-Object of networkx.
            fas (set): Set of feedback edges.
            critical_sources (list): List with sources as strings.
            readded_edgelist (bool): If True, the function returns a list of the readded edges.
        Returns:
            Acyclic graph with possible re-added edges and if desired a list of the readded edges.
    """
    
    aG = aG.copy()
    
    readded_edges = []
    
    for sources in critical_sources:
        sourcenames = nx.get_edge_attributes(G, "source")
        for edge in G.edges():
            u = edge[0]
            v = edge[1]
            if sourcenames[(u,v)] == sources:
                for fasedge in fas:
                    if u == fasedge[0] and v == fasedge[1]:

                        aG.add_edge(u,v, weight=fasedge[2], source=sources)
                        if nx.is_directed_acyclic_graph(aG) == True:
                            readded_edges.append((u, v, fasedge[2], sources))
                            pass
                        else:
                            aG.remove_edge(u,v)
    if readded_edgelist:                       
        return aG, readded_edges
    else:
        return aG
   
def gen_faustgraph(paramlist, special_researchers, tempsyn=False):
    """Genereates a Directed Graph with the date- and relation-elements of the Faust macrogenesis XML files.       
    
    Args:
        paramlist (list): List with the parameters 'approach', 'skipignore' and 'MFAS approach'.
        special_resarchers (dict): Dictionary with sources (string) as keys and their publication year (int) as values.
        tempsyn (bool): If True, the tempsyn-relation-elements will added to the graph.
    Returns:
        Directed Graph with the date- and relation-elements of the Faust macrogenesis XML files.        
    """
    
    approach = paramlist[0]
    skipignore = paramlist[1]
    
    #####
    # preparation of XML file by parsing and collecting specific elements
    #####
    filespath = Path('resources')
    temppre_items = parserutils.xmlparser(filespath)
    date_items = parserutils.xmlparser(filespath, True, skipignore=skipignore)
    
    #####
    # graph for relation-elements
    #####
    
    temppreG = nx.DiGraph()
    for t in temppre_items:
        add_egdes_from_node_list(temppreG, t)
    
    #####
    # graph for date-elements & whole graph G
    #####
    
    if tempsyn:
        tempsyn_items = parserutils.xmlparser(filespath, False, False)
        tempsynG = nx.DiGraph()
        for t in tempsyn_items:
            add_egdes_from_node_list(tempsynG, t, False)    
        tmpG = nx.compose(temppreG, tempsynG)
    else:
        tmpG = temppreG
    if len(paramlist) >= 4:
        datesG = graph_from_dates(date_items, approach, special_researchers, paramlist[3])
    else:
        datesG = graph_from_dates(date_items, approach, special_researchers)
    
    G = nx.compose(tmpG, datesG)
    
    return G