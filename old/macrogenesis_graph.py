# -*- coding: utf-8 -*-
#%%
import utils

from xml.dom import minidom
import networkx as nx
import matplotlib.pyplot as plt
import zipfile
from collections import defaultdict
from pathlib import Path

#basepath = r"C:\Users\Jan\Dropbox\Uni Master Digital Humanities\Semester 1 - Softwareprojekte, Graphentheorie & Weitere\2 Graphentheorie\graphen_projekt\macrogenesis"
#basepath = r"C:\Users\janpa\Dropbox\Uni Master Digital Humanities\Semester 1 - Softwareprojekte, Graphentheorie & Weitere\2 Graphentheorie\graphen_projekt\macrogenesis"

basepath = Path('macrogenesis')
pfad = basepath / "handschriftendatierung_i.xml"
zipfilepath = basepath / "macrogenesis-normalized.zip" 
ziparchive = zipfile.ZipFile(zipfilepath, "r")
g = nx.DiGraph()

"""
    Graph erstellen aus allen Relation-Elementen-Beziehungen
    FEHLT: @name von <relation> --> alle <relation>-Elemente als temp-pre behandelt (Unterscheidung zu temp-syn fehlt)
    FEHLT: absolute Pfade       --> <date>-Elemente
    Ergebnis:
        - date_list :   list-dict mit Form: {"handschrfit1_H.15": [notBefore, notAfter, when]}
"""

date_list = []

for file in ziparchive.namelist():
    if file.endswith(".xml"):
        xml_file = ziparchive.open(file)
        xml_text = minidom.parse(xml_file)
        item_elements = xml_text.getElementsByTagName("item")
        relation_elements = xml_text.getElementsByTagName("relation")
        
        #Absoluten (<date>)
        date_list.append(utils.getHandschriftenDateDict(item_elements))

        #Relativen (<relation>)
        for element in relation_elements:
            temp_node_list = []
            for child in element.childNodes:
                if child.nodeName == "item":
                    uri_value = child.attributes["uri"].value
                    temp_node_list.append(uri_value)
            utils.add_egdes_from_node_list(g, temp_node_list)


print(date_list)
#%%

"""
    Subgraphen-Liste erstellen, bei der jeder Subgraph zyklenfrei ist
"""

graph_list = []   

def recursive_subgraph(graph):
    graph_sub_list = utils.get_directed_subgraphs_list(graph)
    
    for sg in graph_sub_list:
        sg_edge_list = list(sg.edges())
        if nx.is_directed_acyclic_graph(sg):
            sg_edge_list = list(sg.edges())
            graph_list.append(sg_edge_list)
        else:
            left_half, right_half = utils.split_list(sg_edge_list)
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
    Ergebnis:
        - s_ym_handschriften :  dict-dict-list mit Form: {"year": {"month":[top_sort_handschriften_list]}}
"""

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
            
s_ym_handschriften = {k: dict(v) for k, v in sorted_year_handschriften.items()}

print(s_ym_handschriften["1799"])
       
#%%
print(sorted_year_handschriften)
#%%
counter=0
for year, dic in s_ym_handschriften.items():
    tg = nx.DiGraph()
    if counter>= 10:
        break
    
    
    for month, liste in dic.items():
        tg.add_edge(year, month)
        utils.add_egdes_from_node_list(tg, liste)
        tg.add_edge(month, liste[0])
        """
        for handschrift in liste:
            nodes = utils.add_egdes_from_node_list(tg, )
            tg.add_edge(month, ts_list)
            for ts_list in top_sort_list:
                if handschrift == ts_list[0]:
                    #l = [year] + ts_list
                    #print(l)
                    utils.add_egdes_from_node_list(tg, ts_list)
                    tg.add_edge(month, ts_list[0])"""
    
        if tg:
            print(nx.is_tree(tg))
            nx.draw_networkx(tg)
            plt.show()
            #pfad = r"C:\Users\janpa\Dropbox\Uni Master Digital Humanities\Semester 1 - Softwareprojekte, Graphentheorie & Weitere\2 Graphentheorie\graphen_projekt\graphs\tt"
            #pfad = r"C:\Users\Jan\Dropbox\Uni Master Digital Humanities\Semester 1 - Softwareprojekte, Graphentheorie & Weitere\2 Graphentheorie\graphen_projekt\graphs\tt"
            #pfad = r"D:\informatik_programme\graphen_theorie\faust-macrogen-graph\graphs\tt"
            file = "tt" + str(counter) + ".graphml"
            path = "graphs" + "/" + file
            nx.write_graphml(tg, path)
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
#tt7 z.b. immer noch schleifen drinne
#source als kantengewicht hinzufügen (sowohl bei date als auch bei relation)

