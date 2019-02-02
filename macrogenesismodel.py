# -*- coding: utf-8 -*-
from faust-macrogen-graph import relation_items
from pathlib import Path
from xml.dom import minidom
#TODO: etwas umschreiben
def generate_file_list(path, file_extension=".xml"):
    """Returns a Generator with all files that will be processed.
    
    Args:
        path (str): Path to the desired directory.
        file_extension (str): File extension to search for.
    Returns:
        Generator which contains Path objects to all XML files in the given directory and its subdirectories.
    """
    return Path(path).glob("**/*{}".format(file_extension))
    
def xmlparser(path, absolute=False):
    """Parses only xml-files inside a directory.
    
    Args:
        path (str): Path to desired directory.
        absolute (bool): If True, the parser parses <date>-elements, else it parses <relation>-elements.
    Returns:
        
    """
    xmltext_list = []
    parsed_elements = None
    for file in generate_file_list(path):
        xml_text = minidom.parse(str(file))
        if absolute:
            parsed_elements = xml_text.getElementsByTagName("date")
        else:
            parsed_elements = xml_text.getElementsByTagName("relation")
            xmltext_list = relation_items(parsed_elements, xmltext_list)
            
    return xmltext_list
    
filespath = Path('macrogenesis')
#print(generate_file_list(filespath))
print(len(xmlparser(filespath)))



