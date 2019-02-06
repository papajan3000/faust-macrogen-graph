import networkx as nx

def add_egdes_from_node_list(graph, node_list):
    """Add an edge from every node of a list of nodes to the next node in the list with the source as edge attribute.
    
    Args:
        graph (digraph): DiGraph-Object of networkx.
        node_list (tuple): 2-tuple, where the first item is a list of sources and the second item a tuple of nodes in a given order.
    Returns:
        Enhanced input-graph with the nodes and edges of the node_list and the source as edge attribute.
        
    """
    source_name = node_list[0][0]
    node_tuple = node_list[1]
    new_graph = graph
    for index, node in enumerate(node_tuple):
        current_node = node
        next_node = node_tuple[(index + 1) % len(node_tuple)]
        if next_node == node_tuple[0]:
            break
        
        #no loop
        if current_node == next_node:
            pass
        else:
            new_graph.add_edge(current_node, next_node,source=source_name)
    return new_graph   
