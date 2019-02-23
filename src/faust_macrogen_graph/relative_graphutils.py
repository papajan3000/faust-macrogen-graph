#%%
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
