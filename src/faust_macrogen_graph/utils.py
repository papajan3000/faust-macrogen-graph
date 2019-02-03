#TODO: rename utils

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

def relation_items(nodelist, xmltext_list):
    tmp_xmltext_list = xmltext_list
    for element in nodelist:
        tmp_nodelist = []
        for child in element.childNodes:
            if child.nodeName == "item":
                uri_value = child.attributes["uri"].value
                tmp_nodelist.append(uri_value)
        tmp_xmltext_list.append(tmp_nodelist)
        
    return tmp_xmltext_list