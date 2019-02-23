#%%
# -*- coding: utf-8 -*-
from faust_macrogen_graph import parserutils, analyzeutils, eades_fas, absolute_graphutils, relative_graphutils
from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt

#####
# preparation of XML file by parsing and collecting specific elements
#####

filespath = Path('resources')
temppre_items = parserutils.xmlparser(filespath)
tempsyn_items = parserutils.xmlparser(filespath, False, False)
date_items = parserutils.xmlparser(filespath, True)

#%%
#TODO: woanders hin? analyze utils? vielleicht analyzeutils dahingehend umbennen?
import re
def special_witness_generator(item_list):
    """Generate a list with witnesses out of all witnesses whose name doesn't include a publication year.
    
    Args:
        item_list (list): List with date-, temppre- and tempsyn_items.
    Returns:
        List with special witnesses where the publication year can't be extracted from the name.
    """
    witnesses = []
    for items in item_list:
        for item in items:
            witness_list = item[0]
            for witness in witness_list:
                if witness not in witnesses:
                    witnesses.append(witness)
    
    special_witnesses = []
    for w in witnesses:
        match = re.match(r".*([1-3][0-9]{3})", w)
        if match == None:
            special_witnesses.append(w)
    
    
    return special_witnesses


a = special_witness_generator([date_items, tempsyn_items, temppre_items])

print(a)

#%%
#####
# graph for tempsyn <relation>-elements
#####

tempsynG = nx.DiGraph()
for t in tempsyn_items:
    relative_graphutils.add_egdes_from_node_list(tempsynG, t)
#%%
#####
# fas graph tempsyn <relation>-elements
#####
nx.is_directed_acyclic_graph(tempsynG)
    
tempsynG_fas = eades_fas.eades_FAS(tempsynG, True) # seven percent of the edges of tpG are in the FAS

#atempysnG = acyclic tempsyn Graph
atempsynG = tempsynG.copy()
atempsynG.remove_edges_from(tempsynG_fas)
nx.is_directed_acyclic_graph(atempsynG)


#%%
#####
# graph for temppre <relation>-elements
#####

temppreG = nx.DiGraph()
for t in temppre_items:
    relative_graphutils.add_egdes_from_node_list(temppreG, t)

#%%
#####
# fas graph for temppre <relation>-elements
#####
temppreG_fas = eades_fas.eades_FAS(temppreG, True) # seven percent of the edges of tpG are in the FAS

#atemppreG = acyclic temppre Graph
atemppreG = temppreG.copy()
atemppreG.remove_edges_from(temppreG_fas)


#%%
#####
# graph for <date> elements
#####


wissenbach_d = absolute_graphutils.dates_wissenbach(date_items)
        # structure: (manuscript, (date, source))
wissenbach_ds = [(k, wissenbach_d[k]) for k in sorted(wissenbach_d, key=wissenbach_d.get, reverse=False)]
print(wissenbach_ds[1])
#%%
for k, v in absolute_graphutils.dates_vitt(date_items).items():
    print(v)
    
#%%
dateG = absolute_graphutils.graph_from_dates(date_items, "vitt")
print(nx.is_directed_acyclic_graph(dateG))
nx.draw_networkx(dateG)



#%%
#####
# norm the witnesses scores of the witnesses of the new temppre and tempsyn graphs
#####
syn_nws = analyzeutils.get_norm_witness_score(atempsynG)
pre_nws = analyzeutils.get_norm_witness_score(atemppreG)

print("syn-nws: " + str(syn_nws))
print("\n")
print("pre-nws: " + str(pre_nws))

####
# HIER WEITER
# keine doppelten (also keine (v,u) bei (u,v))
#
# Aufgabe a, b, c machen?!
#
#
#%%

fas_relation_overlap = []

for edges in tempsynG_fas:
    if edges in temppreG_fas:
        fas_relation_overlap.append(edges)

#should be empty       
print(fas_relation_overlap)





