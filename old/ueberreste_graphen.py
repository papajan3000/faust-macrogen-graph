# -*- coding: utf-8 -*-
"""
Created on Tue Dec 18 14:17:17 2018

@author: janpa
"""

#%%
#nx.write_graphml(mg, r"C:\Users\Jan\Dropbox\Uni Master Digital Humanities\Semester 1 - Softwareprojekte, Graphentheorie & Weitere\2 Graphentheorie\graphen_projekt\gephigraphen\t1.graphml")


#%%
#nx.draw_networkx(g)
#plt.show()


#%%
#Centralities & Connectivity
"""
ts_list = list(nx.topological_sort(g))

#zahlreiche Verbindungen zu anderen Knoten
dg_cent = nx.degree_centrality(g)   
dg_cent_sorted = [(k, dg_cent[k]) for k in sorted(dg_cent, key=dg_cent.get, reverse=True)]

#hat kurzen Weg zu anderen Knoten des Netzwerks
cl_cent = nx.closeness_centrality(g)
cl_cent_sorted = [(k, cl_cent[k]) for k in sorted(cl_cent, key=cl_cent.get, reverse=True)]

print(dg_cent_sorted)
print("------------------")
print(cl_cent_sorted)
print("------------------")
print(ts_list)
g_connected_strongly = nx.is_strongly_connected(g)
g_connected_weakly = nx.is_weakly_connected(g)
g_attracting_components = nx.is_attracting_component(g)
print(g_connected_strongly)
print(g_connected_weakly)
print(g_attracting_components)
print(nx.is_directed_acyclic_graph(g))
"""
#%%
nx.write_graphml(g, r"C:\Users\Jan\Dropbox\Uni Master Digital Humanities\Semester 1 - Softwareprojekte, Graphentheorie & Weitere\2 Graphentheorie\graphen_projekt\testgraph2.graphml")


#%%
"""
    Alte Ideen


        #Wenn sg_DAG Zyklen enthält, muss er von Zyklen befreit werden --> nur dann topologische Sortierung möglich
        #while sg_DAG == False:
            
   
        #while len(sg.edges) > 1:
            sg = del_random_edge(sg)
            sg_DAG = nx.is_directed_acyclic_graph(sg)
            zeit = time.time() - start_time
            #if zeit >= 100:
                #break
            
nx.draw_networkx(sg)
plt.show()            



        #nx.write_graphml(g, r"C:\Users\Jan\Dropbox\Uni Master Digital Humanities\Semester 1 - Softwareprojekte, Graphentheorie & Weitere\2 Graphentheorie\graphen_projekt\subgraph1.graphml")
        sg_DAG = nx.is_directed_acyclic_graph(sg)

        orig_sg = sg
        
        sg_node_list = list(sg.edges())
        

        
        list1, list2 = split_list(sg_node_list)
        
        g2 = nx.DiGraph()
        g2.add_edges_from(list1)

        print(nx.is_directed_acyclic_graph(g2))
        a = get_

        
        
#nur ein Subgraph hat mehr als sieben Knoten (nämlich 494)

for sg in g_sub_list:
    if len(sg.nodes()) >= 7:
        g_sub_list.remove(sg)

    directed_subgraphs_list(g2)
    
   """
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
                utils.add_egdes_from_node_list(tg, ts_list)
                tg.add_edge(year, ts_list[0])
    if tg:
        print(nx.is_tree(tg))
        nx.draw_networkx(tg)
        plt.show()
        #pfad = r"C:\Users\janpa\Dropbox\Uni Master Digital Humanities\Semester 1 - Softwareprojekte, Graphentheorie & Weitere\2 Graphentheorie\graphen_projekt\graphs\tt"
        #pfad = r"C:\Users\Jan\Dropbox\Uni Master Digital Humanities\Semester 1 - Softwareprojekte, Graphentheorie & Weitere\2 Graphentheorie\graphen_projekt\graphs\tt"
        pfad = "graphs\tt"
        pfad2 = pfad + str(counter) + ".graphml"
        nx.write_graphml(tg, pfad2)
    counter+=1

#%%
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