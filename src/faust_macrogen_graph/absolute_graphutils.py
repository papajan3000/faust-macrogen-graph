#%%
#TODO: docstrings for all überprüfen
#TODO: ^
#TODO: |
#TODO: Begriff witnesses austauschen!!!! sind ja keine Zeugen, sind "Quellen"
import networkx as nx
from collections import Counter
import re
from datetime import datetime

def year_comparison(manuscript, existing_manuscript_source, source_name):
    """Checks if the year of an already existing manuscript source is greater or smaller than the year of a different source for the same 
        manuscript. The greater year will be returned. If the year doesn't appear inside the witnesses name, the year of the special
        witnesses dictionary will be taken (the dates are taken from the following website: http://faustedition.net/bibliography).
    
    Args:
        manuscript (string): String of the manuscript.
        existing_manuscript_source (string): Witness of the manuscript already in a dictionary.
        source_name (string): Possible different witness for the same manuscript.
        
    Returns:
        False if the year inside the existing_manuscript_source string is greater than the year in the source_name string.
    """
    greater = False
    
    special_witnesses = {'faust://bibliography/gsa-datenbank' : 1950, 
                         'faust://self' : 2000, 
                         'faust://bibliography/inventare_2_2': 2011, 
                         'faust://bibliography/aa_duw_2': 1974,
                         'faust://print/faustedition/J.2': 1887, 
                         'faust://bibliography/quz_1': 1966, 
                         'faust://bibliography/quz_2': 1982, 
                         'faust://bibliography/quz_3': 1986,
                         'faust://bibliography/quz_4': 1984,
                         'faust://bibliography/wa_I_13_2': 1901, 
                         'faust://bibliography/wa_I_14' : 1887, 
                         'faust://bibliography/wa_I_15_2' : 1888, 
                         'faust://bibliography/wa_I_53': 1914,
                         'faust://bibliography/wa_IV_13' : 1893}

    existing_year = re.match(r".*([1-3][0-9]{3})", existing_manuscript_source)
    actual_year = re.match(r".*([1-3][0-9]{3})", source_name)
            
    if existing_year is not None and actual_year is not None:
        existing_year = str(existing_year.group(1))
        actual_year = str(actual_year.group(1))
        
        if existing_year > actual_year:
            greater = False
        elif actual_year >= existing_year:
            greater = True
        
    elif existing_year is None and actual_year is not None:
        if existing_manuscript_source in special_witnesses:
            existing_year = special_witnesses[existing_manuscript_source]
            actual_year = str(actual_year.group(1))
            
            if existing_year > actual_year:
                greater = False
            elif actual_year >= existing_year:
                greater = True
                
    elif existing_year is not None and actual_year is None:
        if source_name in special_witnesses:
            existing_year = str(existing_year.group(1))
            actual_year = special_witnesses[source_name]
            
            if existing_year > actual_year:
                greater = False
            elif actual_year >= existing_year:
                greater = True

    return greater
     

def dates_wissenbach(date_items):
    """Generate a dictionary following the approach of Wissenbach (see: resources/vitt_macrogen.pdf, p. 12) where the middle of two dates
        is concatenated with a manuscript instead of multiple dates.
        
        Args:
            date_items (list): List of tupels with the following structure: ([source], (manuscript), {notBefore: year, notAfter: year, when: year}).
        Returns:
            Dictionary with the manuscripts as keys and 2-tuples as values with the structure (middle of date, source).
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
            mid_date = datetime.strptime(when, '%Y-%m-%d')
        elif notafter == "-" and notbefore != "-":
            mid_date = datetime.strptime(notbefore, '%Y-%m-%d')
        elif notbefore == "-" and notafter != "-":
            mid_date = datetime.strptime(notafter, '%Y-%m-%d')
        elif notbefore != "-" and notafter != "-":
            nb_date = datetime.strptime(notbefore, '%Y-%m-%d')
            na_date = datetime.strptime(notafter, '%Y-%m-%d')

            mid_date = nb_date + (na_date - nb_date) / 2
        
        #not adding falsely tagged date-elements (6 elements exist)
        if mid_date != "-":
            if manuscript in wissenbach_dict:
                existing_manuscript_source = wissenbach_dict[manuscript][1]
                
                #if there is a conflict between two witnesses who classify the manuscript date differently, the newer one will be taken
                greater = year_comparison(manuscript, existing_manuscript_source, source_name)
                
                if greater:
                    wissenbach_dict[manuscript] = (mid_date, source_name)
                else:
                    pass
            else:
                wissenbach_dict[manuscript] = (mid_date, source_name)
                
    return wissenbach_dict

#TODO: überarbeiten
def dates_vitt(date_items):
    """Generate a dictionary following the approach of Vitt (see: resources/vitt_macrogen.pdf, p. 13) where the manuscripts and the dates
        of the manuscripts are treated as nodes. If an exact date for a manuscript exists (@when), the manuscript gets a higher weight-value.
        
        Args:
            date_items (list): List of tupels with the following structure: ([source], (manuscript), {notBefore: year, notAfter: year, when: year}).
        Returns:
            Dictionary with the manuscripts as keys and 2-,3- or 4-tuples as values with the structure (start_date, source_name) or
            (start_date, source_name, 10.0) or (start_date, source_name, 1.0, end_date).
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
            start_date = datetime.strptime(when, '%Y-%m-%d')
            vitt_dict[manuscript] = (start_date, source_name, 10.0)
        elif notafter == "-" and notbefore != "-":
            start_date = datetime.strptime(notbefore, '%Y-%m-%d')
            vitt_dict[manuscript] = (start_date, source_name)
        elif notbefore == "-" and notafter != "-":
            start_date = datetime.strptime(notafter, '%Y-%m-%d')
            vitt_dict[manuscript] = (start_date, source_name)
        elif notbefore != "-" and notafter != "-":
            start_date = datetime.strptime(notbefore, '%Y-%m-%d')
            end_date = datetime.strptime(notafter, '%Y-%m-%d')
            vitt_dict[manuscript] = (start_date, source_name, 1.0, end_date)
    
    return vitt_dict

#TODO: bearbeiten
def dates_paulus(date_items, notbeforedate=True):
    """Generate a dictionary following one of two approach of Paulus (author of this project) where the manuscripts and the dates
        of the manuscripts are treated as nodes but only one date is connected with manuscript (there is a choice between @notBefore
        or @notAfter dates). If an exact date for a manuscript exists (@when), the manuscript gets a higher weight-value.
        
        Args:
            date_items (list): List of tupels with the following structure: ([source], (manuscript), {notBefore: year, notAfter: year, when: year}).
            notbeforedate (bool): If True, the manuscripts will be connected with the @notBefore-Date, else with the @notAfter-Date.
        Returns:
            Dictionary with the manuscripts as keys and 2- or 3-tuples as values with the structure (start_date, source_name) or
            (start_date, source_name, 10.0).
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
                start_date = datetime.strptime(notbefore, '%Y-%m-%d')
            elif when != "-":
                start_date = datetime.strptime(when, '%Y-%m-%d')
            #if notBefore and when were not provieded with a date, notAfter will be taken instead
            elif notafter != "-" and notbefore == "-":
                start_date = datetime.strptime(notafter, '%Y-%m-%d')
        else:
            if notafter != "-":
                start_date = datetime.strptime(notafter, '%Y-%m-%d')
            elif when != "-":
                start_date = datetime.strptime(when, '%Y-%m-%d')
            #if notAfter and when were not provieded with a date, notBefore will be taken instead
            elif notbefore != "-" and notafter == "-":
                start_date = datetime.strptime(notbefore, '%Y-%m-%d')
        
        
        #not adding falsely tagged date-elements (6 elements exist)
        if start_date != "-":
            #if there is a conflict between two witnesses who classify the manuscript date differently, the newer one will be taken
            if manuscript in paulus_dict:
                existing_manuscript_source = paulus_dict[manuscript][1]
                greater = year_comparison(manuscript, existing_manuscript_source, source_name)
                
                if greater:
                    if when != "-":
                        paulus_dict[manuscript] = (start_date, source_name, 10.0)
                    else:
                        paulus_dict[manuscript] = (start_date, source_name)
                else:
                    pass
            else:
                if when != "-":
                    paulus_dict[manuscript] = (start_date, source_name, 10.0)
                else:
                    paulus_dict[manuscript] = (start_date, source_name)
            
    return paulus_dict

#TODO: docstring
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
    """Generates a graph out of date_items by connecting nodes through edges based on one of four different systems (= approaches).
    
    Args:
        date_items (list): 3-tuple, where the first item is a list of sources, the second item a tuple of nodes in a given order 
                            and the third items is a dictionary with the keys "notBefore", "notAfter" and "when".
        approach (string): One of the following four approaches: wissenbach, vitt, paulus-1, paulus-2.
    Returns:
        A Directed Graph Object of networkx with edges and nodes based on one of the four approaches.
    """
    G = nx.DiGraph()
    
    if approach == "wissenbach":
        wissenbach_d = dates_wissenbach(date_items)
        wissenbach_ds = [(k, wissenbach_d[k]) for k in sorted(wissenbach_d, key=wissenbach_d.get, reverse=False)]
        G = add_edges_from_dates_list(G, wissenbach_ds)
    elif approach == "vitt":
        vitt_d = dates_vitt(date_items)
        vitt_ds = [(k, vitt_d[k]) for k in sorted(vitt_d, key=vitt_d.get, reverse=False)]
        G = add_edges_from_dates_list(G, vitt_ds)
    elif approach == "paulus-1":
        paulus1_d = dates_paulus(date_items)
        paulus1_ds = [(k, paulus1_d[k]) for k in sorted(paulus1_d, key=paulus1_d.get, reverse=False)]
        G = add_edges_from_dates_list(G, paulus1_ds)
    elif approach == "paulus-2":
        paulus2_d = dates_paulus(date_items, False)
        paulus2_ds = [(k, paulus2_d[k]) for k in sorted(paulus2_d, key=paulus2_d.get, reverse=False)]
        G = add_edges_from_dates_list(G, paulus2_ds)
    
    return G
    
