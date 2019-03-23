from collections import Counter
import re
import pandas as pd
from faust_macrogen_graph import graphutils, eades_fas
from collections import OrderedDict
from itertools import permutations

#####
# functions for representing and analyzing source features
#####

def gen_frequencyfas(G):
    """Computes a DataFrame where all sources of the feedback edges are concatenated with the frequency they appear in the FAS.
    
    Args:
        G (DiGraph): DiGraph-Object of networkx.
    Returns:
        DataFrame with the sources of the FAS as index and their frequency within the FAS as column.
    """
    G_fas = eades_fas.eades_FAS(G, True)
    
    #frequency of the researcher as manuscript source
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
    fasfrequency_df = fasfrequency_df.rename(columns={"index":"source", 0: "fas_frequency"})
    fasfrequency_df.set_index("source", inplace=True)
    
    return fasfrequency_df


def dataframe_from_column(df, metacol, extractcol):
    """Extracts DataFrames of specific columns of another DataFrame and generates a new DataFrame.
    
    Args:
        df (DataFrame): The DataFrame whereof the DataFrames will be extracted.
        metacol (string): Column name of df, where the DataFrames are stored.
        extractcol (string): Column name of the extracted DataFrame.
    Returns:
        Extracted DataFrame from another DataFrame.
    """
    d = {}
    for idx, dataframe in enumerate(df[metacol]):
        source = list(df.index)
        extractdf = dict(dataframe[extractcol])
        d[source[idx]] = extractdf

    return pd.DataFrame(d)


def get_source_year(G, special_researchers):
    """Returns dictionary with the edge sources of a graph as keys and their publication year as values, extracted from a string
        or a special dictionary.
    
    Args:
        G (DiGraph): DiGraph-Object of networkx.
        special_resarchers (dict): Dictionary with sources (string) as keys and their publication year (int) as values. 
    Returns:
        Dictionary with the sources as keys and their publication year as values.
    """    
    source_year = {}
    
    for edge in G.edges():
        edge_data = G.get_edge_data(edge[0], edge[1])
        source = edge_data["source"]
        if source in source_year:
            pass
        else:
            if source in special_researchers:
                year = special_researchers[source]
            else:
                year = re.match(r".*([1-3][0-9]{3})", str(source))
                if year is not None:
                    year = year.group(1)
                else:
                    year = 1000
            
            source_year[source] = int(year)
        
    return source_year


def get_research_score(G):
    """Parses through the source-attribute of the Graph edges and returns a Counter with a frequency score assigned to each researcher.
    
    Args:
        G (DiGraph): DiGraph-Object of networkx.
    Returns:
        Counter with a frequency score assigned to each researcher.
    """
    research_score = Counter()
    for edge in G.edges():
        edge_data = G.get_edge_data(edge[0], edge[1])
        source = edge_data["source"]
        research_score[source] += 1
    return research_score


def get_norm_research_score(G, special_researchers, min_range=1770, max_range=2017):
    """Normalizes the score of a frequency of a researchers work. The score is computed as following: 
            Number of the researchers work mentioned in the macrogenesis * normalized year of publication of researchers work about Faust
            e.g.: Bohnenkamp 1994 --> 94 * ((1994 - 1770) / (2017 - 1770)) = 94 * 0.9068825910931174 = 85.24696356275304
        The goal of the normalization is to generate a number between 0 and 1 as coefficent (or weight) and multiplying this with the publication year
        of the work to give older researchers work less weight in the context of a comparison between two possible conflicting statements of researchers 
        about a different dating of manuscripts.
        
    Args:
        G (DiGraph): DiGraph-Object of networkx.
        special_resarchers (dict): Dictionary with sources (string) as keys and their publication year (int) as values. 
        min_range (int): Lower border of the normalization function.
        max_range (int): Upper border of the normalization function.
    Returns:
        Counter with a normalized score assigned to each researcher.
    """
    research_score = dict(get_research_score(G))
    norm_research_score = {}
    

    for key, value in research_score.items():
        if key in special_researchers:
            year = special_researchers[key]
        else:
            year = re.match(r".*([1-3][0-9]{3})", str(key))
            if year is not None:
                year = year.group(1)
            else:
                year = 1000
                
        normalized_year = (int(year) - min_range) / (max_range - min_range) #range(1700, 2020), normalized to be between 0 and 1
        norm_research_score[key] = value * normalized_year
    return norm_research_score

def gen_critical_sources(G, norm_percent_fas):
    """Computes a dictionary with sources of the FAS as keys and the size of the FAS without the sources as values.
    
    Args:
        G (DiGraph): DiGraph-Object of networkx.
        norm_percent_fas (dict): Dictionary with sources as keys and normed percentage of their edges within the FAS as values.        
    Return:
        Dictionary with sources of the FAS as keys and the size of the FAS without the sources as values.
    """
    
    critical_sources_fas = {}
    
    for critical_source, v in norm_percent_fas.items():
        nG = G.copy()
        for edge in list(nG.edges()):
            edge_data = nG.get_edge_data(edge[0], edge[1])
            if edge_data["source"] == critical_source:
                nG.remove_edge(edge[0], edge[1])
        nG_fas = eades_fas.eades_FAS(nG, True)
        critical_sources_fas[critical_source] = len(nG_fas)
    
    return critical_sources_fas


def get_normdf(G, special_researchers, dropna=True, min_range=1770, max_range=2017):
    """Computes a DataFrame with the sources of G as index and the norm_percent_fas-scores and norm_year_frequency-scores as columns.
    
    Args:
        G (DiGraph): DiGraph-Object of networkx.
        special_resarchers (dict): Dictionary with sources (string) as keys and their publication year (int) as values.
        dropna (bool): If True, the rows with NaN values will be dropped.
        min_range (int): Lower border of the normalization function.
        max_range (int): Upper border of the normalization function.
    Returns:
        DataFrame with the sources of G as index and the norm_percent_fas-scores and norm_year_frequency-scores as columns.
    """
    G_fas_frequency = gen_frequencyfas(G)
    
    norm_research_scores = get_norm_research_score(G, special_researchers, min_range, max_range)
    sorted_norm_research_scores = {k: norm_research_scores[k] for k in sorted(norm_research_scores, key=norm_research_scores.get, reverse=True)}
    
    norm_research_df = pd.DataFrame(sorted_norm_research_scores.items(), columns=["source", "norm_year_frequency"])
    norm_research_df.set_index("source", inplace=True)
    
    norm_percent_fas = (G_fas_frequency["fas_frequency"] / norm_research_df["norm_year_frequency"]) * 100
    norm_percentfas_df = pd.DataFrame(norm_percent_fas)
    norm_percentfas_df = norm_percentfas_df.rename(columns={0:"norm_percent_fas"})
    norm_df = norm_research_df.join(norm_percentfas_df, on="source")
    if dropna:
        norm_df = norm_df.dropna()
    norm_df = norm_df.sort_values(by="norm_percent_fas", ascending=False)
    
    return norm_df


#####
# functions for FAS minimizing
#####

def minimize_source_removal(G, remaining_fas_size=0):
    """Computes a DataFrame where the sources of the FAS are the indices and the columns. The FAS is reduced
        step by step by choosing a source and parsing through the source list (without the selected source)
        and remove the source until the FAS reaches a given remaining size. Every source that has been removed
        during the iteration will get an "1" value within the DataFrame, every other source, which wasn't necessary
        for the reducing of the FAS gets a "0" value. 
    
    Args:
        G (DiGraph): DiGraph-Object of networkx.
        remaining_fas_size (int): Integer which states how big the remaining FAS can be.
    Return:
        DataFrame with "1" values for source, which are important for the FAS, and "0"-values for sources, which can possible be
        re-added without inducing new cycles.
    """
    
    fasfrequency_df = gen_frequencyfas(G)
    sourcelist = list(fasfrequency_df.index)
    df = pd.DataFrame(0, index=sourcelist, columns=sourcelist)
    
    for source in sourcelist:
        
        nG = graphutils.remove_edges_by_source(G.copy(), source)
        nG_fas = eades_fas.eades_FAS(nG, True)
        df[source][source] = 1
        
        if len(nG_fas) > remaining_fas_size:
            withoutsource = [e for i,e in enumerate(sourcelist) if e != source]
            
            for element in withoutsource:
                nG = graphutils.remove_edges_by_source(nG, element)
                nG_fas = eades_fas.eades_FAS(nG, True)
                df[element][source] = 1
                
                if len(nG_fas) <= remaining_fas_size:
                    break
    
    df.index.name = "source"
    return df

def minimize_fas_by_source_removal(G):
    """Computes a DataFrame where the sources of the FAS are the indices and the columns. Each cell of the DataFrame shows,
        how many edges are in the FAS after the removal of the index- and column-sources.
    
    Args:
       G (DiGraph): DiGraph-Object of networkx.
    Returns:
        DataFrame with the reduced fas size of the respective index- and column-sources.
    """
    
    fasfrequency_df = gen_frequencyfas(G)
    sourcelist = list(fasfrequency_df.index)
    df = pd.DataFrame(0, index=sourcelist, columns=sourcelist)
    
    for source in sourcelist:
        
        nG = graphutils.remove_edges_by_source(G.copy(), source)
        nG_fas = eades_fas.eades_FAS(nG, True)
        df[source][source] = len(list(nG_fas))
        
        withoutsource = [e for i,e in enumerate(sourcelist) if e != source]
            
        for element in withoutsource:
            nnG = graphutils.remove_edges_by_source(nG.copy(), element)
            nnG_fas = eades_fas.eades_FAS(nnG, True)
            df[element][source] = len(list(nnG_fas))
            
    df.index.name = "source"
    return df


def find_optimal_order(G, minimize_rm_source_df, remaining_fas_size):
    """Computes a Dictionary with order-IDs as keys and dictionaries as values which in turn have the keys "fas_size", "opt_order" and
        "orig_order". The function takes the sources of the FAS of G and tries to find an optimal order of edges which size is minimal for 
        a given minimimum remaining FAS. For this, all permutations of the six most important FAS sources are tried out 
        (6 (= 720 combinations) is the maximum parameter to be calculated for the permutations in order to maintain a good performance).
    Args:
        G (DiGraph): DiGraph-Object of networkx.
        minimize_rm_source_df (DataFrame): DataFrame with the sources of the FAS as indices and columns and the FAS size without the 
                                            sources as cell value.
        remaining_fas_size (int): Desired maximimu size of the FAS after the removal of sources.                                
    Returns:
        Dictionary with order-IDs as keys and dictionaries as values which in turn have the keys "fas_size", "opt_order" and
        "orig_order"
    """
    # choosing the elements with the lowest value of a row cell
    sourcelist = list(dict(minimize_rm_source_df.min()[:6]).keys())
    
    optimal_order_dict = {}
    permutationlist = list(permutations(sourcelist, len(sourcelist)))
    order_ID = 0
    
    for l in permutationlist:
        nG = G.copy()
        nG_fas = list(range(1,100)) #random big nG_fas which will be overwritten
        order = []
        for source in l:
            if len(nG_fas) <= remaining_fas_size:
                break
            else:
                nG = graphutils.remove_edges_by_source(nG, source)
                nG_fas = eades_fas.eades_FAS(nG, True)
                order.append(source)

        optimal_order_dict[order_ID] = {"fas_size": len(nG_fas), "opt_order": order, "orig_order": l}
        order_ID += 1
        
    return optimal_order_dict

def minimum_of_optimal_order(optimal_order_dict, min_fas=True):
    """Parses through a dictionary and finds the minimum FAS with a minimum order or a minimum order with a mimimum FAS.
    
    Args:
        optimal_order_dict (dict): Dictionary with numbers as keys and dictionaries with the keys "fas_size", "opt_order" 
                                    and "orig_order" as values,
        min_fas (bool): If True, the order with the smallest fas_size with the smallest optimal order will be choosen, 
                        else the smallest optimal order with the smallest fas_size.               
    Returns:
        List with the smallest FAS as first element and the smallest optimal order as second element.           
    """
    minimum = [100, ["", "", "", "", "", ""]]
    if min_fas:
        for k, dictionary in optimal_order_dict.items():
            if minimum[0] > dictionary["fas_size"]:
                minimum[0] = dictionary["fas_size"]
                minimum[1] = dictionary["opt_order"]
            elif minimum[0] == dictionary["fas_size"] and len(dictionary["opt_order"]) < len(minimum[1]):
                minimum[0] = dictionary["fas_size"]
                minimum[1] = dictionary["opt_order"]
    else:
        for k, dictionary in optimal_order_dict.items():
            if len(minimum[1]) > len(dictionary["opt_order"]):
                minimum[0] = dictionary["fas_size"]
                minimum[1] = dictionary["opt_order"]
            elif minimum[0] == dictionary["fas_size"] and len(dictionary["opt_order"]) < len(minimum[1]):
                minimum[0] = dictionary["fas_size"]
                minimum[1] = dictionary["opt_order"]
            
    return minimum

def remove_uncritical_sources(G, G_fas, G_fas_frequency, fas_df):
    """Computes a list of sources who could possible removed from the Graph to make it acyclic and the reduced size of the FAS 
        without the uncritical sources. This function is based on the assumption that a FAS could be reduced by removing
        edges of the cyclic graph by sources in a specific order.
    Args:
        G (DiGraph): DiGraph-Object of networkx.
        G_fas (set): Set of feedback edges of G.
        G_fas_frequency: DataFrame with the sources of the FAS as index and their frequency within the FAS as column.
        fas_df: DataFrame with the sources of the FAS as index and columns and tha value 0 or 1 if the source is 
                necessary for the minimize source removal.
    Returns:
        List of sources who could possible removed from the Graph to make it acyclic and the reduced size of the FAS 
        without the uncritical sources.
    """
    Gfasdict = dict(fas_df.sum(axis=1))
    G_minfas = min(Gfasdict, key=Gfasdict.get) #row with the lowest total value
    minlGfasdict = dict(fas_df.loc[G_minfas]) #dict of the row
    
    tmp_G = G.copy()
    
    reduced_fas = 0
    uncritical_sources = []
    for k,v in minlGfasdict.items():
        if v == 1:
            tmp_G = graphutils.remove_edges_by_source(tmp_G, k)
        else:
            reduced_fas += G_fas_frequency.loc[k]["fas_frequency"]
            uncritical_sources.append(k)
                  
    tmp_G_fas = eades_fas.eades_FAS(tmp_G, True)
    if tmp_G_fas == set():
        print("The FAS could be theoretical reduced from " + str(len(G_fas)) 
              + " edges to " + str((len(G_fas) - reduced_fas)) + " edges (decrease of " 
             + str(int((reduced_fas / len(G_fas)) * 100)) + "%).")
    else:
        print("The FAS is still there and contains " + str(len(tmp_G_fas)) + " edges.")
        
    return uncritical_sources, reduced_fas

#####
# special functions 
#####

def special_research_generator(item_list):
    """Generates a list with researchers out of all researchers whose name doesn't include a publication year.
    
    Args:
        item_list (list): List with date-, temppre- and tempsyn_items.
    Returns:
        List with special researchers where the publication year can't be extracted from the name.
    """
    researchers = []
    for items in item_list:
        for item in items:
            research_list = item[0]
            for research in research_list:
                if research not in researchers:
                    researchers.append(research)
    
    special_researchers = []
    for r in researchers:
        match = re.match(r".*([1-3][0-9]{3})", r)
        if match == None:
            special_researchers.append(r)

    return special_researchers