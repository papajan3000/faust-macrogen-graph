# -*- coding: utf-8 -*-
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
    
def xmlparser(path):
    for file in generate_file_list(path):
        xml_text = minidom.parse(str(file))
        item_elements = xml_text.getElementsByTagName("item")
        print(item_elements)
    
filespath = Path('macrogenesis')

print(xmlparser(filespath))


