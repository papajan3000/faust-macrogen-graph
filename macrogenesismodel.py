# -*- coding: utf-8 -*-
from faust_macrogen_graph import parserutils, graphutils
from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt

filespath = Path('resources')
items = parserutils.xmlparser(filespath)
print(items[2])
#%%
#####
# graph for temppre <relation>-elements
#####

#TODO: remove the enumerate
G = nx.DiGraph()
for idx, t in enumerate(items):
    if idx < 100000:
        graphutils.add_egdes_from_node_list(G, t)
    else:
        break
  
nx.draw_networkx(G)
plt.show()
nx.write_graphml(G, "graphs/g4.graphml")

#%%
