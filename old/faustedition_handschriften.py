# -*- coding: utf-8 -*-
#%%
from xml.dom import minidom
from datetime import datetime
import networkx as nx
import matplotlib.pyplot as plt

#import os
#import sys

pfad = r"C:\Users\Jan\Dropbox\Uni Master Digital Humanities\Semester 1 - Softwareprojekte, Graphentheorie & Weitere\2 Graphentheorie\graphen_projekt\macrogenesis\handschriftendatierung_i.xml"
#pfad = r"C:\Users\janpa\Dropbox\Uni Master Digital Humanities\Semester 1 - Softwareprojekte, Graphentheorie & Weitere\2 Graphentheorie\graphen_projekt\macrogenesis\handschriftendatierung_i.xml"


xml_text = minidom.parse(pfad)
item_elements = xml_text.getElementsByTagName("item")



def getHandschriftenDateDict(item_elements):

    handschriften_date_dict = {}
    
    for element in item_elements:
        uri_value = element.attributes["uri"].value
        parent_node = element.parentNode
        parent_node_name = element.parentNode.nodeName
        if parent_node_name == "date":
            attribute_names = parent_node.attributes.keys()
            temp_handschrift_date_dict = {}
            if "i_" not in uri_value:
                handschrift_name = uri_value.rsplit('/', 1)[-1]
            elif r"/" == uri_value[-1:]:
                handschrift_name = uri_value.rsplit('/', 3)[-3] + "/" + uri_value.rsplit('/', 2)[-2] + "/" + uri_value.rsplit('/', 1)[-1] 
            else:
                handschrift_name = uri_value.rsplit('/', 2)[-2] + "/" + uri_value.rsplit('/', 1)[-1] 
            temp_dict = {}
            for key in attribute_names:
                if key == "notBefore":
                    temp_dict["notBefore"] = parent_node.attributes["notBefore"].value
                elif key == "notAfter":
                    temp_dict["notAfter"] = parent_node.attributes["notAfter"].value
            temp_handschrift_date_dict[handschrift_name] = temp_dict
            
            handschriften_date_dict.update(temp_handschrift_date_dict)
        
    return handschriften_date_dict    

handschriften_date_dict = getHandschriftenDateDict(item_elements)

print(handschriften_date_dict)
#print("----------------------")


#%%

def sortDictToSpecificDate(handschriften_date_dict, specificdate, outputdict=True):

    notBefore_list = []
    
    for key, value in handschriften_date_dict.items():
        for datekey, datevalue in value.items():
            if datekey == specificdate:
                temp_l = [key]
                temp_l.append(datevalue)
                """
                splitted_date = datevalue.split("-") #Liste ["Jahr", "Monat", "Tag"]
                splitted_date = tuple(splitted_date)
                """
                notBefore_list.append(temp_l)
                temp_l = []
        
    notBefore_list.sort(key=lambda L: datetime.strptime(L[1], '%Y-%m-%d'))

    if outputdict == True:
        notBefore_dict = {}
        
        for element in notBefore_list:
            value = element[1]
            key = element[0]
            notBefore_dict[key] = value
        
        return notBefore_dict
    else:
        return notBefore_list

print("----------------------")
notBefore_dict = sortDictToSpecificDate(handschriften_date_dict, "notBefore")
notAfter_dict = sortDictToSpecificDate(handschriften_date_dict, "notAfter")
print(notBefore_dict)

#%%

#unnütz?
def dateInTupel(string):
    splitted_date = string.split("-") #Liste ["Jahr", "Monat", "Tag"]
    return tuple(splitted_date)

g = nx.Graph()

days_handschriften_dict = {}

for b_key, b_value in notBefore_dict.items():
    for a_key, a_value in notAfter_dict.items():
        if b_key == a_key:
            b_date = datetime.strptime(b_value, '%Y-%m-%d')
            a_date = datetime.strptime(a_value, '%Y-%m-%d')
            days_of_handschrift_date = a_date - b_date
            days_of_handschrift_date = days_of_handschrift_date.days
            
            days_handschriften_dict[b_key] = days_of_handschrift_date
            
print(days_handschriften_dict)            
            
#g.add_node("handschriftendatierung_i")

for i in range(1790, 1830):
    g.add_node(i)



for b_key, b_value in notBefore_dict.items():

    splitted_date = b_value.split("-") #Liste ["Jahr", "Monat", "Tag"]
    splitted_date = tuple(splitted_date)
    print(splitted_date[0])
    g.add_edge(b_key, splitted_date[0])

"""
counter = 0

for key, value in days_handschriften_dict.items():
    if counter >= 7:
        break
    g.add_edge("handschriftendatierung_i", key, weight=value)
    counter += 1
""" 

pos = nx.shell_layout(g)
nx.draw_networkx(g, pos)
plt.show() 

#%%
        
#nx.write_graphml(g, r"C:\Users\Jan\Dropbox\Uni Master Digital Humanities\Semester 1 - Softwareprojekte, Graphentheorie & Weitere\2 Graphentheorie\graphen_projekt\testgraph.graphml")
#a = r"C:\Users\janpa\Dropbox\Uni Master Digital Humanities\Semester 1 - Softwareprojekte, Graphentheorie & Weitere\2 Graphentheorie\graphen_projekt\testgraph.graphml"
#nx.write_graphml(g, a)
########
#IDEE ##
########

#temp-pre durch gerichteten Graphen darstellen
#schwach zusammenhängende Komponenten angucken!
#in stark zusammenhängenden widersprechen sich Knoten, vor allem bei Zyklen (a->b->c->a)
#DAG = Directed A










