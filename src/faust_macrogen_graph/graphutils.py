#%%
#TODO: docstrings
import networkx as nx
from collections import Counter
import re
from datetime import datetime


#TODO: weg
from faust_macrogen_graph import parserutils
from pathlib import Path
import matplotlib.pyplot as plt

"""
    <!--  J.2 : Erscheinungsdatum 07-04-1808 (Nr. 84), 13-04-1808 (Nr. 89), 03-05-1808 (Nr. 108) -->
    <date from="1808-04-07" to="1808-05-03">
        <source uri="faust://self"/>
        <source uri="faust://print/faustedition/J.2"/>
        <item uri="faust://document/faustedition/J.2"/>
    </date>
"""

def add_egdes_from_node_list(G, node_list):
    """Add an edge from every node of a list of nodes to the next node in the list with the source as edge attribute.
    
    Args:
        G (DiGraph): DiGraph-Object of networkx.
        node_list (list): list with 2-tuples, where the first item is a list of sources and the second item a tuple of nodes in a given order.
    Returns:
        Enhanced input-graph with the nodes and edges of the node_list and the source as edge attribute.
    """
    #only first source is taken if more than one source exist
    source_name = node_list[0][0]
    node_tuple = node_list[1]
    nG = G
    for index, node in enumerate(node_tuple):
        current_node = node
        next_node = node_tuple[(index + 1) % len(node_tuple)]
        if next_node == node_tuple[0]:
            break
        
        #no loop
        if current_node == next_node:
            pass
        else:
            nG.add_edge(current_node, next_node, weight=1.0, source=source_name)
    return nG

def dates_wissenbach(date_items):
    """
    
        Returns:
            Dictionary 
    """
    
    wissenbach_dict = {}
    
    for item in date_items:
        source_name = item[0][0]
        manuscript = item[1][0]
        dates_dict = item[2]
        
        notbefore = dates_dict["notBefore"]
        notafter = dates_dict["notAfter"]
        when = dates_dict["when"]
        
        mid_date = "-"
        
        if when != "-":
            mid_date = datetime.strptime(dates_dict["when"], '%Y-%m-%d')
        elif notafter == "-" and notbefore != "-":
            mid_date = datetime.strptime(dates_dict["notBefore"], '%Y-%m-%d')
        elif notbefore == "-" and notafter != "-":
            mid_date = datetime.strptime(dates_dict["notAfter"], '%Y-%m-%d')
        elif notbefore != "-" and notafter != "-":
            nb_date = datetime.strptime(notbefore, '%Y-%m-%d')
            na_date = datetime.strptime(notafter, '%Y-%m-%d')

            mid_date = nb_date + (na_date - nb_date) / 2
        
        #not adding falsely tagged date-elements (6 elements exist)
        if mid_date != "-":
            #if there is a conflict between two witnesses who classify the manuscript date differently, the newer one will be taken
            if manuscript in wissenbach_dict:
                existing_manuscript_source = wissenbach_dict[manuscript][1]
                
                existing_year = re.match(r".*([1-3][0-9]{3})", existing_manuscript_source)
                actual_year = re.match(r".*([1-3][0-9]{3})", source_name)
                
                if existing_year is not None and actual_year is not None:
                    existing_year = str(existing_year.group(1))
                    actual_year = str(actual_year.group(1))
                
                    if existing_year > actual_year:
                        pass
                    elif actual_year >= existing_year:
                        wissenbach_dict[manuscript] = (mid_date, source_name)
            else:
                wissenbach_dict[manuscript] = (mid_date, source_name)
            
            
    return wissenbach_dict


def dates_vitt(date_items):
    """
    """
    vitt_dict = {}
    
    for item in date_items:
        source_name = item[0][0]
        manuscript = item[1][0]
        dates_dict = item[2]
        
        notbefore = dates_dict["notBefore"]
        notafter = dates_dict["notAfter"]
        when = dates_dict["when"]
        
        start_date = "-"
        end_date = "-"
        
        if when != "-":
            start_date = datetime.strptime(dates_dict["when"], '%Y-%m-%d')
            vitt_dict[manuscript] = (start_date, source_name, 100.0)
        elif notafter == "-" and notbefore != "-":
            start_date = datetime.strptime(dates_dict["notBefore"], '%Y-%m-%d')
            vitt_dict[manuscript] = (start_date, source_name)
        elif notbefore == "-" and notafter != "-":
            start_date = datetime.strptime(dates_dict["notAfter"], '%Y-%m-%d')
            vitt_dict[manuscript] = (start_date, source_name)
        elif notbefore != "-" and notafter != "-":
            start_date = datetime.strptime(notbefore, '%Y-%m-%d')
            end_date = datetime.strptime(notafter, '%Y-%m-%d')
            #TODO: zu lazy, vernünftiges datenmodell
            vitt_dict[manuscript] = (start_date, source_name, 1.0, end_date)
    
    return vitt_dict



def dates_paulus(date_items, notbeforedate=True):
    """
    notBefore + when
    """
    
    
    paulus_dict = {}
    
    for item in date_items:
        source_name = item[0][0]
        manuscript = item[1][0]
        dates_dict = item[2]
        
        notbefore = dates_dict["notBefore"]
        notafter = dates_dict["notAfter"]
        when = dates_dict["when"]
        
        start_date = "-"
        
        if notbeforedate:
            if notbefore != "-":
                start_date = datetime.strptime(dates_dict["notBefore"], '%Y-%m-%d')
            elif when != "-":
                start_date = datetime.strptime(dates_dict["when"], '%Y-%m-%d')
            #if notBefore and when were not provieded with a date, notAfter will be taken instead
            elif notafter != "-" and notbefore == "-":
                start_date = datetime.strptime(dates_dict["notAfter"], '%Y-%m-%d')
        else:
            if notafter != "-":
                start_date = datetime.strptime(dates_dict["notAfter"], '%Y-%m-%d')
            elif when != "-":
                start_date = datetime.strptime(dates_dict["when"], '%Y-%m-%d')
            #if notAfter and when were not provieded with a date, notBefore will be taken instead
            elif notbefore != "-" and notafter == "-":
                start_date = datetime.strptime(dates_dict["notBefore"], '%Y-%m-%d')
        
        
        #not adding falsely tagged date-elements (6 elements exist)
        if start_date != "-":
            #if there is a conflict between two witnesses who classify the manuscript date differently, the newer one will be taken
            if manuscript in paulus_dict:
                existing_manuscript_source = paulus_dict[manuscript][1]
                
                existing_year = re.match(r".*([1-3][0-9]{3})", existing_manuscript_source)
                actual_year = re.match(r".*([1-3][0-9]{3})", source_name)
                
                if existing_year is not None and actual_year is not None:
                    existing_year = str(existing_year.group(1))
                    actual_year = str(actual_year.group(1))
                
                    if existing_year > actual_year:
                        pass
                    elif actual_year >= existing_year:
                        if when != "-":
                            paulus_dict[manuscript] = (start_date, source_name, 100.0)
                        else:
                            paulus_dict[manuscript] = (start_date, source_name)
            else:
                if when != "-":
                    paulus_dict[manuscript] = (start_date, source_name, 100.0)
                else:
                    paulus_dict[manuscript] = (start_date, source_name)
            
    return paulus_dict

def add_edges_from_dates_list(G, dates_list):
    """
    """
    nG = G
    for t in dates_list:
        
        manuscript = t[0]
        date_item = t[1][0]
        source_name = t[1][1]

        #in case of special case of Paulus approaches where @when attribute gets a higher weight
        if len(t[1]) == 3:
            nG.add_edge(str(date_item), manuscript, weight=t[1][2], source=source_name)
        elif len(t[1]) == 4:
            nG.add_edge(str(date_item), manuscript, weight=1.0, source=source_name)
            nG.add_edge(manuscript, str(t[1][3]), weight=1.0, source=source_name)
        else:
            nG.add_edge(str(date_item), manuscript, weight=1.0, source=source_name)
    return nG
        
        
def graph_from_dates(date_items, approach):
    #TODO: 
    """
    See resources/vitt_macrogen.pdf p. 12.
    
    Args:
        date_items (list): 3-tuple, where the first item is a list of sources, the second item a tuple of nodes in a given order 
                        and the third items is a dictionary with the keys "notBefore", "notAfter" and "when"
    """
    G = nx.DiGraph()
    
    if approach == "wissenbach":
        
        wissenbach_d = dates_wissenbach(date_items)
        # structure: (manuscript, (date, source))
        wissenbach_ds = [(k, wissenbach_d[k]) for k in sorted(wissenbach_d, key=wissenbach_d.get, reverse=False)]
        G = add_edges_from_dates_list(G, wissenbach_ds)
    elif approach == "vitt":
        vitt_d = dates_vitt(date_items)
        vitt_ds = [(k, vitt_d[k]) for k in sorted(vitt_d, key=vitt_d.get, reverse=False)]
        G = add_edges_from_dates_list(G, vitt_ds)
    #only "notBefore" and "when" nodes, but "when"-nodes got higher weight
    elif approach == "paulus-1":
        paulus1_d = dates_paulus(date_items)
        # structure: (manuscript, (date, source)) or (manuscript, (date, source, 100.0))
        paulus1_ds = [(k, paulus1_d[k]) for k in sorted(paulus1_d, key=paulus1_d.get, reverse=False)]
        G = add_edges_from_dates_list(G, paulus1_ds)
    #only "notAfter" and "when" nodes, but "when"-nodes got higher weight
    elif approach == "paulus-2":
        paulus2_d = dates_paulus(date_items, False)
        # structure: (manuscript, (date, source)) or (manuscript, (date, source, 100.0))
        paulus2_ds = [(k, paulus2_d[k]) for k in sorted(paulus2_d, key=paulus2_d.get, reverse=False)]
        G = add_edges_from_dates_list(G, paulus2_ds)

    
    return G
    

#%%

def get_witness_score(G):
    """Parse through the source-attribute of Graph edges and return a Counter with a score assigned to each witness.
    
    Args:
        G (DiGraph): DiGraph-Object of networkx.
    Returns:
        Counter with a score assigned to each witness.
    """
    witness_score = Counter()
    for edge in G.edges():
        edge_data = G.get_edge_data(edge[0], edge[1])
        source = edge_data["source"]
        witness_score[source] += 1
    return witness_score



def get_norm_witness_score(G, min_range=1700, max_range=2020):
    """Normalize the score of a given Counter of witnesses and their score. The score is computed as following: 
            Number of the witnesses work mentioned in the macrogenesis * normalized year of publication of witnessess work about Faust
            e.g.: Bohnenkamp 1994 --> 94 * ((1994 - 1700) / (2020 - 1700)) = 94 * 0.91875 = 86.3625
        The goal of the normalization is to generate a number between 0 and 1 as coefficent to give older witnesses work less weight in the context
        of a comparison between two possible conflicting statements of witnesses about a different dating of manuscripts.
        
    Args:
        G (DiGraph): DiGraph-Object of networkx.
        min_range (int): Lower border of the normalization function.
        max_range (int): Upper border of the normalization function.
    Returns:
        Counter with a normalized score assigned to each witness.
    """
    witness_score = get_witness_score(G)
    #gsa-datenbank random value because no real year determinable
    #faust//self same
    special_witnesses = {'faust://bibliography/wa_I_15_2': 1888, 
                         'faust://bibliography/inventare_2_2' : 2011,
                         'faust://bibliography/gsa-datenbank' : 1950,
                         'faust://self' : 2000}
    
    for key, value in dict(witness_score).items():
        if key in special_witnesses:
            year = special_witnesses[key]
        else:
            year = re.match(r".*([1-3][0-9]{3})", str(key))
            if year is not None:
                year = year.group(1)
                
        normalized_year = (int(year) - min_range) / (max_range - min_range) #range(1700, 2020), normalized to be between 0 and 1
        witness_score[key] = value * normalized_year
    return witness_score