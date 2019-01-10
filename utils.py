import networkx as nx
import random

def getHandschriftenDateDict(item_elements):
    handschriften_date_dict = {}
    for element in item_elements:
        uri_value = element.attributes["uri"].value
        parent_node = element.parentNode
        parent_node_name = element.parentNode.nodeName
        if parent_node_name == "date":
            attribute_names = parent_node.attributes.keys()
            temp_handschrift_date_dict = {}
            handschrift_name = uri_value
            
            temp_list = [None] * 3
            for key in attribute_names:
                if key == "notBefore":
                    temp_list[0] = parent_node.attributes["notBefore"].value
                elif key == "notAfter":
                    temp_list[1] = parent_node.attributes["notAfter"].value
                elif key == "when":
                    temp_list[2] = parent_node.attributes["when"].value
            temp_handschrift_date_dict[handschrift_name] = temp_list
            handschriften_date_dict.update(temp_handschrift_date_dict)
    return handschriften_date_dict  

def add_egdes_from_node_list(graph, node_list):
    new_graph = graph
    for index, node in enumerate(node_list):
        current_node = node
        next_node = node_list[(index + 1) % len(node_list)]
        if next_node == node_list[0]:
            break
        
        if current_node == next_node: #keine Schleife
            pass
        else:
            new_graph.add_edge(current_node, next_node)
    return new_graph   

def get_directed_subgraphs_list(graph):
    l = []
    ug = graph.to_undirected()
    ug_components = nx.connected_components(ug)
    for c in ug_components:
        subg = graph.subgraph(c).copy()
        l.append(subg)
    return l

def del_random_edge(graph):
    edges_list = graph.edges()
    r_number = 1
    randomsample = random.sample(edges_list, r_number)
    graph.remove_nodes_from(randomsample)
    return graph
    
def split_list(a_list):
    half = len(a_list) // 2
    return a_list[:half], a_list[half:]

