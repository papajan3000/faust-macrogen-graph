#%%
from faust_macrogen_graph import parserutils, analyzeutils, graphutils, eades_fas
from pathlib import Path
import pandas as pd
from collections import Counter, OrderedDict
import networkx as nx

#TODO: docstring
#TODO: überarbeiten
def gengraph(paramlist, special_researchers, tempsyn=False):
    """
    
    Args:
        paramlist (list): List with the parameters 'approach', 'skipignore' and 'MFAS approach'.
        special_resarchers (dict): Dictionary with sources (string) as keys and their publication year (int) as values.
        tempsyn (bool): If True, the tempsyn-relation-elements will added to the graph.
    Returns:
        
    """
    
    approach = paramlist[0]
    skipignore = paramlist[1]
    
    
    #####
    # preparation of XML file by parsing and collecting specific elements
    #####
    filespath = Path('resources')
    temppre_items = parserutils.xmlparser(filespath)
    date_items = parserutils.xmlparser(filespath, True, skipignore=skipignore)
    
    temppreG = nx.DiGraph()
    for t in temppre_items:
        graphutils.add_egdes_from_node_list(temppreG, t)
    
    #####
    # graph for <date> elements & whole graph G
    #####
    
    if tempsyn:
        tempsyn_items = parserutils.xmlparser(filespath, False, False)
        tempsynG = nx.DiGraph()
        for t in tempsyn_items:
            graphutils.add_egdes_from_node_list(tempsynG, t, False)    
        tmpG = nx.compose(temppreG, tempsynG)
    else:
        tmpG = temppreG
    if len(paramlist) >= 4:
        datesG = graphutils.graph_from_dates(date_items, approach, special_researchers, paramlist[3])
    else:
        datesG = graphutils.graph_from_dates(date_items, approach, special_researchers)
    
    G = nx.compose(tmpG, datesG)
    
    return G
    


#TODO: edit docstring and whole function
#TODO: insgesamt mal überarbeiten
#TODO: rename
def fas_test(paramlist, special_researchers, tempsyn=False):
    """
    Args:
        paramlist (list): List with the parameters 'approach', 'skipignore' and 'MFAS approach'.
        special_resarchers (dict): Dictionary with sources (string) as keys and their publication year (int) as values.
        tempsyn (bool): If True, the tempsyn-relation-elements will added to the graph.
    Returns:
        
    """
    
    ###########################################################################
    ###########################################################################
    # preparation & creation of graph
    ###########################################################################
    ###########################################################################
    
    #{fas, edges, nodes, cycles, df}
    fas_test_dict = {}    
    fas_algorithm = paramlist[2]

    G = gengraph(paramlist, special_researchers, tempsyn)
    G_fas = eades_fas.eades_FAS(G, fas_algorithm)
    
    #####
    # adding to the fas_test_dict
    #####
    fas_test_dict["fas"] = len(G_fas)
    fas_test_dict["edges"] = len(G.edges())
    fas_test_dict["nodes"] = len(G.nodes())
    fas_test_dict["nodeslist"] = list(G.nodes())
    fas_test_dict["cycles"] = len(list(nx.simple_cycles(G)))
    
    ###########################################################################
    ###########################################################################
    # analyzation
    ###########################################################################
    ###########################################################################
    year_scores = analyzeutils.get_source_year(G, special_researchers)
    year_df = pd.DataFrame(year_scores.items(), columns=["source", "year"])
    year_df.set_index("source", inplace=True)
    
    #df with research count scores
    research_scores = analyzeutils.get_research_score(G)
    sorted_research_scores = {k: research_scores[k] 
                                  for k in sorted(research_scores, key=research_scores.get, reverse=True)}
    research_df = pd.DataFrame(sorted_research_scores.items(), columns=["source", "year_frequency"])
    research_df.set_index("source", inplace=True)
    
    #df with normed research count scores
    norm_research_scores = analyzeutils.get_norm_research_score(G, special_researchers, 1770, 2017)
    sorted_norm_research_scores = {k: norm_research_scores[k]
                                  for k in sorted(norm_research_scores, key=norm_research_scores.get, reverse=True)}
    
    norm_research_df = pd.DataFrame(sorted_norm_research_scores.items(), columns=["source", "norm_year_frequency"])
    norm_research_df.set_index("source", inplace=True)
        
    #combinig the three dfs
    source_df = research_df.join(norm_research_df)
    
    #adding df with publication year of the source to the source_df
    year_scores = analyzeutils.get_source_year(G, special_researchers)
    year_df = pd.DataFrame(year_scores.items(), columns=["source", "pub_year"])
    year_df.set_index("source", inplace=True)
    
    source_df = source_df.join(year_df)
    
    
    
    fas_source_counter = Counter()
    for edge in G_fas:
        if G.has_edge(edge[0], edge[1]):
            edge_data = G.get_edge_data(edge[0], edge[1])
            key = edge_data["source"]
            if fas_source_counter[key]:
                fas_source_counter[key] += 1
            else:
                fas_source_counter[key] = 1
    
                
    fasfrequency_df = pd.DataFrame.from_dict(OrderedDict(fas_source_counter.most_common()), 
                                             orient="index").reset_index()
    fasfrequency_df = fasfrequency_df.rename(columns={"index":"source", 0:"fas_frequency"})
    fasfrequency_df.set_index("source", inplace=True)
    
    df = source_df.join(fasfrequency_df)
    df = df.dropna()
    
    percent_fas = (df["fas_frequency"] / df["year_frequency"]) * 100
    norm_percent_fas = (df["fas_frequency"] / df["norm_year_frequency"]) * 100
    percentfas_df = pd.concat([percent_fas, norm_percent_fas], axis=1, sort=True)
    percentfas_df = percentfas_df.rename(columns={0:"percent_fas", 1:"norm_percent_fas"})
    percentfas_df.sort_values(by="percent_fas", ascending=False)
    df = df.join(percentfas_df, on="source")
    
    
    fas_test_dict["source_df"] = source_df
    fas_test_dict["fasfrequency_df"] = fasfrequency_df
    fas_test_dict["percentfas_df"] = percentfas_df
    
    
    return fas_test_dict
