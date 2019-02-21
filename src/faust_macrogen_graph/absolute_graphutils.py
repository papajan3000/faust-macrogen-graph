#%%
#TODO: docstrings
import networkx as nx
from collections import Counter
import re
from datetime import datetime

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
    
