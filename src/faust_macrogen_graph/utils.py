from xml.dom import minidom

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