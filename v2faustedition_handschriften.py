# -*- coding: utf-8 -*-
#%%
from xml.dom import minidom
from datetime import datetime
import time
import networkx as nx
import matplotlib.pyplot as plt
import zipfile
import random
from collections import defaultdict


basepfad = r"C:\Users\Jan\Dropbox\Uni Master Digital Humanities\Semester 1 - Softwareprojekte, Graphentheorie & Weitere\2 Graphentheorie\graphen_projekt\macrogenesis"
#basepfad = r"C:\Users\janpa\Dropbox\Uni Master Digital Humanities\Semester 1 - Softwareprojekte, Graphentheorie & Weitere\2 Graphentheorie\graphen_projekt\macrogenesis"

pfad = basepfad + "\handschriftendatierung_i.xml"
zipfilepfad = basepfad + "\macrogenesis-normalized.zip" 

ziparchive = zipfile.ZipFile(zipfilepfad, "r")

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
            """
            temp_dict = {}
            for key in attribute_names:
                if key == "notBefore":
                    temp_dict["notBefore"] = parent_node.attributes["notBefore"].value
                elif key == "notAfter":
                    temp_dict["notAfter"] = parent_node.attributes["notAfter"].value
            temp_handschrift_date_dict[handschrift_name] = temp_dict
            """
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
    #print(randomsample)
    graph.remove_nodes_from(randomsample)
    
    return graph
    
def split_list(a_list):
    half = len(a_list) // 2
    return a_list[:half], a_list[half:]

g = nx.DiGraph()

"""
    Graph erstellen aus allen Relation-Elementen-Beziehungen
    FEHLT: @name von <relation> --> alle <relation>-Elemente als temp-pre behandelt (Unterscheidung zu temp-syn fehlt)
    FEHLT: absolute Pfade       --> <date>-Elemente
"""

date_list = []

for file in ziparchive.namelist():
    if file.endswith(".xml"):
        xml_file = ziparchive.open(file)
        xml_text = minidom.parse(xml_file)
        item_elements = xml_text.getElementsByTagName("item")
        relation_elements = xml_text.getElementsByTagName("relation")
        
        #Absoluten (<date>)
        date_list.append(getHandschriftenDateDict(item_elements))
        

        #Relativen (<relation>)
        for element in relation_elements:
            temp_node_list = []
            for child in element.childNodes:
                if child.nodeName == "item":
                    uri_value = child.attributes["uri"].value
                    temp_node_list.append(uri_value)
                    
            add_egdes_from_node_list(g, temp_node_list)


#%%

"""
    Subgraphen-Liste erstellen, bei der jeder Subgraph zyklenfrei ist
"""

graph_list = []   
                
def recursive_subgraph(graph):
    graph_sub_list = get_directed_subgraphs_list(graph)
    
    for sg in graph_sub_list:
        sg_edge_list = list(sg.edges())
        if nx.is_directed_acyclic_graph(sg):
            sg_edge_list = list(sg.edges())
            graph_list.append(sg_edge_list)
        else:
            left_half, right_half = split_list(sg_edge_list)
            l_g = nx.DiGraph()
            r_g = nx.DiGraph()
            l_g.add_edges_from(left_half)
            r_g.add_edges_from(right_half)
            
            recursive_subgraph(l_g)
            recursive_subgraph(r_g)
            
            
recursive_subgraph(g)


top_sort_list = []

for edge_list in graph_list:
    subgraph = nx.DiGraph()
    subgraph.add_edges_from(edge_list)
    ts_list = list(nx.topological_sort(subgraph))
    top_sort_list.append(ts_list)


print(top_sort_list)

#%%
"""
    date_list sortieren
    --> date_list besteht aus dictionaries, die jeweils eins der xml-Dokumente repräsentieren
    --> dictionaries bestehen aus Handschriften als keys und NotBefore-, NotAfter- und When-Werten in einer Liste als values
"""
print(date_list)

#%%
sorted_year_handschriften = defaultdict(lambda : defaultdict(list))

for dic in date_list:
    for handschrift, dates in dic.items():
        notBefore = dates[0]
        if notBefore != None:
            splitted_date = notBefore.split("-")
            year = splitted_date[0]
            month = splitted_date[1]
            day = splitted_date[2]
            sorted_year_handschriften[year][month].append(handschrift)
            
print(sorted_year_handschriften)
print("----")

#%%
s_ym_handschriften = {k: dict(v) for k, v in sorted_year_handschriften.items()}

print(s_ym_handschriften["1800"])
       
#%%
counter=0
for year, liste in sorted_year_handschriften.items():
    tg = nx.DiGraph()
    if counter>= 10:
        break
    for element in liste:
        for ts_list in top_sort_list:
            if element == ts_list[0]:
                #l = [year] + ts_list
                #print(l)
                add_egdes_from_node_list(tg, ts_list)
                tg.add_edge(year, ts_list[0])
    if tg:
        print(nx.is_tree(tg))
        nx.draw_networkx(tg)
        plt.show()
        #pfad = r"C:\Users\janpa\Dropbox\Uni Master Digital Humanities\Semester 1 - Softwareprojekte, Graphentheorie & Weitere\2 Graphentheorie\graphen_projekt\gephigraphen\tt"
        pfad = r"C:\Users\Jan\Dropbox\Uni Master Digital Humanities\Semester 1 - Softwareprojekte, Graphentheorie & Weitere\2 Graphentheorie\graphen_projekt\gephigraphen\tt"
        pfad2 = pfad + str(counter) + ".graphml"
        nx.write_graphml(tg, pfad2)
    counter+=1

    



#%%
"""
    Wir haben:
        top_sort_list (<relation>)
        sorted_year_handschriften (<date>)
        
    Testweise Graphen ausgeben
"""

mg = nx.DiGraph()

for year in list(range(1770,1890)):
    year = str(year)
    if year in sorted_year_handschriften:
        handschrift_list = sorted_year_handschriften[year]
        for handschrift in handschrift_list:
            mg.add_edge(year, handschrift)
        
nx.draw_networkx(mg)
plt.show()

#evtl. TO-DO: sind Quellen widersprüchlich? Wieviele?
#wieviel stark, schwach zusammenhängende Komponenten
