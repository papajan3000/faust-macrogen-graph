import networkx as nx

def add_egdes_from_node_list(graph, node_list):
    """Add an edge from every node of a list of nodes to the next node in the list.
    
    Args:
        graph (digraph): DiGraph-Object of networkx.
        node_list (tuple): tuple of nodes in a given order.
    Returns:
        Enhanced input-graph with the nodes and edges of the node_list.
        
    """
    new_graph = graph
    for index, node in enumerate(node_list):
        current_node = node
        next_node = node_list[(index + 1) % len(node_list)]
        if next_node == node_list[0]:
            break
        
        #no loop
        if current_node == next_node:
            pass
        else:
            new_graph.add_edge(current_node, next_node)
    return new_graph   

