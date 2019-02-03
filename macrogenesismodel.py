# -*- coding: utf-8 -*-
from faust_macrogen_graph import utils
from pathlib import Path
from xml.dom import minidom

    
def xmlparser(path, absolute=False):
    """Parses only xml-files inside a directory.
    
    Args:
        path (str): Path to desired directory.
        absolute (bool): If True, the parser parses <date>-elements, else it parses <relation>-elements.
    Returns:
        
    """
    xmltext_list = []
    parsed_elements = None
    for file in utils.generate_file_list(path):
        xml_text = minidom.parse(str(file))
        if absolute:
            parsed_elements = xml_text.getElementsByTagName("date")
        else:
            parsed_elements = xml_text.getElementsByTagName("relation")
            xmltext_list = utils.relation_items(parsed_elements, xmltext_list)
            
    return xmltext_list
    
filespath = Path('resources')
#print(generate_file_list(filespath))
print(len(xmlparser(filespath)))



