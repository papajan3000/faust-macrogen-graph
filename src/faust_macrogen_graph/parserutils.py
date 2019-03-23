from pathlib import Path
from xml.dom import minidom

def generate_file_list(path, file_extension=".xml"):
    """Returns a Generator with all files that will be processed.
    
    Args:
        path (str): Path to the desired directory.
        file_extension (str): File extension to search for.
    Returns:
        Generator which contains Path objects to all XML files in the given directory and its subdirectories.
    """
    return Path(path).glob("**/*{}".format(file_extension))


def date_items(nodelist, items, skipignore):
    """Expand the a list of items with a tuple for every <date>-element which is represented by the structure
        ([source], (@uri of <item>-element), {"notBefore": date, "notAfter": date, "when": date}). Non-existing
        attributes of <date> will be marked with a "-".
    
    Args:
        nodelist (NodeList): NodeList of <date>-elements of a XML document.
        items (list): List of <date>-element-tuples.
        skipignore (bool): If True, <date>-elements with the @ignore=yes attribute will be skipped.
    Example:
        >>>print(date_items(nodelist, items))
       [(['faust://bibliography/bohnenkamp1994'], ('faust://document/faustedition/T_1_H.0',), {'notBefore': '1810-11-04', 'notAfter': '1812-12-01', 'when': '-'}), 
       (['faust://bibliography/bohnenkamp1994'], ('faust://document/faustedition/T_1_H.1',), {'notBefore': '1812-10-20', 'notAfter': '1812-12-01', 'when': '-'})]
    Returns:
        Edited list of items with newly appended tuples.
    """
    tmp_items = items
    
    for element in nodelist:
        if skipignore:
            if "ignore" in element.attributes and element.getAttribute("ignore") == "yes":
                continue

        tmp_sources = []
        tmp_nodes = []
        tmp_dates = {}
        tmp_nodelist = []
        
        for child in element.childNodes:      
            if child.nodeName == "source":
                tmp_sources.append(child.attributes["uri"].value)
            
        #if no source is given
        if not tmp_sources:
            tmp_sources.append("no source")
        
        for child in element.childNodes:
            if child.nodeName == "item":
                tmp_nodes.append(child.attributes["uri"].value)
        
        if element.getAttribute("notBefore"):
            tmp_dates["notBefore"] = element.getAttribute("notBefore")
        else:
            #@from attributes will be treated as @notBefore attributes
            if element.getAttribute("from"):
                tmp_dates["notBefore"] = element.getAttribute("from")
            else:
                tmp_dates["notBefore"] = "-"
            
        if element.getAttribute("notAfter"):
            tmp_dates["notAfter"] = element.getAttribute("notAfter")
        else:
            #@to attributes will be treated as @notAfter attributes
            if element.getAttribute("to"):
                tmp_dates["notAfter"] = element.getAttribute("to")
            else:
                tmp_dates["notAfter"] = "-"
        
        if element.getAttribute("when"):
            tmp_dates["when"] = element.getAttribute("when")
        else:
            tmp_dates["when"] = "-"
            
    
        tmp_nodelist.append(tmp_sources)    
        tmp_nodelist.append(tuple(tmp_nodes))     
        tmp_nodelist.append(tmp_dates)              
        tmp_items.append(tuple(tmp_nodelist))
    
    return tmp_items


def relation_items(nodelist, items, temppre):
    """Expand the a list of items with a tuple for every <relation>-element which is represented by the structure
        ([source], (@uri of first <item>-element, @uri of second <item>-element)).
    
    Args:
        nodelist (NodeList): NodeList of <relation>-elements of a XML document.
        items (list): List of <relation>-element-tuples.
        temppre (bool): If True, the function only adds temp-pre child-items, else it adds temp-syn child-items.
    Example:
        >>>print(relation_items(nodelist, items, True))
        [(['faust://bibliography/bohnenkamp1994'], ('faust://document/faustedition/H_P9', 'faust://document/bohnenkamp/H_P9a')), 
        (['faust://bibliography/bohnenkamp1994'], ('faust://document/faustedition/1_H.10', 'faust://document/faustedition/H_P27'))]
    Returns:
        Edited list of items with newly appended tuples.
    """
    
    if temppre:
        relation_name = "temp-pre"
    else:
        relation_name = "temp-syn"
    
    tmp_items = items
    for element in nodelist:
        if element.getAttribute("name") == relation_name:
            tmp_sources = []
            tmp_nodelist = []
            tmp_nodes = []
            for child in element.childNodes:      
                if child.nodeName == "source":
                    tmp_sources.append(child.attributes["uri"].value)
            
            #if no source is given
            if not tmp_sources:
                tmp_sources.append("no source")
                    
            for child in element.childNodes:
                if child.nodeName == "item":
                    tmp_nodes.append(child.attributes["uri"].value)
            
            tmp_nodelist.append(tmp_sources)    
            tmp_nodelist.append(tuple(tmp_nodes))                   
            tmp_items.append(tuple(tmp_nodelist))
        
    return tmp_items

def xmlparser(path, absolute=False, temppre=True, skipignore=False):
    """Parses only XML files inside a directory and returns a list with tuples which contain either relative dates or 
        absolute dates of a manuscript.
    
    Args:
        path (str): Path to desired directory.
        absolute (bool): If True, the parser parses <date>-elements, else it parses <relation>-elements.
        temppre (bool): If True, the function only adds temp-pre child-items, else it adds temp-syn child-items.
        skipignore (bool): If True, <date>-elements with the @ignore=yes attribute will be skipped.
    Returns:
        List with tupels which contain either relative dates or absolute dates of a manuscript.
   
    """
    items = []
    parsed_elements = None
    for file in generate_file_list(path):
        xml_text = minidom.parse(str(file))
        if absolute:
            parsed_elements = xml_text.getElementsByTagName("date")
            items = date_items(parsed_elements, items, skipignore)
        else:
            parsed_elements = xml_text.getElementsByTagName("relation")
            items = relation_items(parsed_elements, items, temppre)

    return items