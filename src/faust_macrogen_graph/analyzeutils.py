from collections import Counter
import re
import pandas as pd


def dataframe_from_column(df, metacol, extractcol):
    """Extract DataFrames of specific columns of another DataFrame and generate a new DataFrame.
    
    Args:
        df (DataFrame): The DataFrame whereof the DataFrames will be extracted.
        metacol (string): Column name of df, where the DataFrames are stored.
        extractcol (string): Column name of the extracted DataFrame.
    Returns:
        Extracted DataFramefrom another DataFrame.
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
    """Parse through the source-attribute of Graph edges and return a Counter with a frequency score assigned to each researcher.
    
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
    """Normalize the score of a given Counter of researchers and their score. The score is computed as following: 
            Number of the researchers work mentioned in the macrogenesis * normalized year of publication of researchers work about Faust
            e.g.: Bohnenkamp 1994 --> 94 * ((1994 - 1770) / (2017 - 1770)) = 94 * 0.9068825910931174 = 85.24696356275304
        The goal of the normalization is to generate a number between 0 and 1 as coefficent to give older researchers work less weight in the context
        of a comparison between two possible conflicting statements of researchers about a different dating of manuscripts.
        
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