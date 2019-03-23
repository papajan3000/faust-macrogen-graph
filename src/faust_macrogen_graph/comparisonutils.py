#%%
from faust_macrogen_graph import parserutils, analyzeutils, graphutils, eades_fas
from pathlib import Path
import pandas as pd
from collections import Counter, OrderedDict
import networkx as nx


    
def gen_feature_dict(paramlist, special_researchers, tempsyn=False):
    """Computes a dictionary with graph and source features as key-value-pairs.
    
    Args:
        paramlist (list): List with the parameters 'approach', 'skipignore' and 'MFAS approach'.
        special_resarchers (dict): Dictionary with sources (string) as keys and their publication year (int) as values.
        tempsyn (bool): If True, the tempsyn-relation-elements will added to the graph.
    Returns:
        Dictionary with graph and source features as key-value-pairs.
    """
    
    #####
    # preparation & creation of graph
    #####
    
    #{fas, edges, nodes, cycles, df}
    feature_dict = {}    
    fas_algorithm = paramlist[2]

    G = graphutils.gen_faustgraph(paramlist, special_researchers, tempsyn)
    G_fas = eades_fas.eades_FAS(G, fas_algorithm)
    
    #####
    # adding graph features to the feature_dict
    #####
    feature_dict["fas"] = len(G_fas)
    feature_dict["edges"] = len(G.edges())
    feature_dict["nodes"] = len(G.nodes())
    feature_dict["nodeslist"] = list(G.nodes())
    feature_dict["cycles"] = len(list(nx.simple_cycles(G)))
    
    #####
    # analysis
    #####
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
    
    
    feature_dict["source_df"] = source_df
    feature_dict["fasfrequency_df"] = fasfrequency_df
    feature_dict["percentfas_df"] = percentfas_df
    
    
    return feature_dict

def compare_approaches(approaches, special_researchers, temppre=False):
    """Computes a DataFrame where the number of nodes, edges, cycles and feedback edges of each approach from the
        approaches list will be listed.
    Args:
        approaches (list): List with the approaches names as strings.
        special_resarchers (dict): Dictionary with sources (string) as keys and their publication year (int) as values. 
        temppre (bool): If True, the graph for the approaches will be computed by the combination of 
                        the temppre- and the dates-graph, if False, only the dates-graph.
    Return:
        DataFrame with the approaches as index and the features "n nodes", "n edges", "n cycles" and "n feedback edges" as columns.
    """

    approaches_graphs = {}
    approaches_fas =  {}
    
    filespath = Path('resources')
    date_items = parserutils.xmlparser(filespath, True, skipignore=False)
    
    for approach in approaches:
        
        if temppre:
            temppre_items = parserutils.xmlparser(filespath)
            temppreG = nx.DiGraph()
            for t in temppre_items:
                graphutils.add_egdes_from_node_list(temppreG, t)
                
            datesG = graphutils.graph_from_dates(date_items, approach, special_researchers)
            G = nx.compose(temppreG, datesG)
            
        else:
            G = graphutils.graph_from_dates(date_items, approach, special_researchers)
        
        approaches_graphs[approach] = G
        G_fas = eades_fas.eades_FAS(G, True)
        aG = G.copy()
        aG.remove_edges_from(G_fas)
    
        approaches_fas[approach] = G_fas
    
    graphs_approaches = {}
    columns = ["n nodes", "n edges", "n cycles", "n feedback edges"]
    
    for k, v in approaches_graphs.items():
        graphs_approaches[k] = [len(v.nodes()), len(v.edges()), len(list(nx.simple_cycles(v))), len(approaches_fas[k])]
    
    approach_df = pd.DataFrame(graphs_approaches)
    approach_df = approach_df.T
    approach_df.columns = columns
    
    return approach_df
