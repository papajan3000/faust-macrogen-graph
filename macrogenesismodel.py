# -*- coding: utf-8 -*-
from faust_macrogen_graph import parserutils, graphutils, eades_fas
from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt


filespath = Path('resources')
items = parserutils.xmlparser(filespath)
#%%
#####
# graph for temppre <relation>-elements
#####


G = nx.DiGraph()
for t in items:
    graphutils.add_egdes_from_node_list(G, t)

nx.draw_networkx(G)
plt.show()
#nx.write_graphml(G, "graphs/g5.graphml")

#%%
# seven percent of the edges are in the FAS

fas = eades_fas.eades_FAS(G, True)
print(type(fas))

####
# HIER WEITER
# keine doppeltn (also keine (v,u) bei (u,v))
#
# Aufgabe a, b, c machen?!
#
#

#%%

G2 = G.copy()

G2.remove_edges_from(fas)

c = 0
for component in nx.connected_component_subgraphs(G.to_undirected()):
    c += len(component.edges())
    print(len(component.edges()))
print("-")
print(c)
#%%
print(len(G.edges()))
print(len(G2.edges()))

print(nx.is_directed_acyclic_graph(G2))



