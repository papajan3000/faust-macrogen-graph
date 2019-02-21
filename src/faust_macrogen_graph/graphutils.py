#%%
#TODO: docstrings
import networkx as nx
from collections import Counter
import re
from datetime import datetime


def get_witness_score(G):
    """Parse through the source-attribute of Graph edges and return a Counter with a score assigned to each witness.
    
    Args:
        G (DiGraph): DiGraph-Object of networkx.
    Returns:
        Counter with a score assigned to each witness.
    """
    witness_score = Counter()
    for edge in G.edges():
        edge_data = G.get_edge_data(edge[0], edge[1])
        source = edge_data["source"]
        witness_score[source] += 1
    return witness_score



def get_norm_witness_score(G, min_range=1700, max_range=2020):
    """Normalize the score of a given Counter of witnesses and their score. The score is computed as following: 
            Number of the witnesses work mentioned in the macrogenesis * normalized year of publication of witnessess work about Faust
            e.g.: Bohnenkamp 1994 --> 94 * ((1994 - 1700) / (2020 - 1700)) = 94 * 0.91875 = 86.3625
        The goal of the normalization is to generate a number between 0 and 1 as coefficent to give older witnesses work less weight in the context
        of a comparison between two possible conflicting statements of witnesses about a different dating of manuscripts.
        
    Args:
        G (DiGraph): DiGraph-Object of networkx.
        min_range (int): Lower border of the normalization function.
        max_range (int): Upper border of the normalization function.
    Returns:
        Counter with a normalized score assigned to each witness.
    """
    witness_score = get_witness_score(G)
    #gsa-datenbank random value because no real year determinable
    #faust//self same
    special_witnesses = {'faust://bibliography/wa_I_15_2': 1888, 
                         'faust://bibliography/inventare_2_2' : 2011,
                         'faust://bibliography/gsa-datenbank' : 1950,
                         'faust://self' : 2000}
    
    for key, value in dict(witness_score).items():
        if key in special_witnesses:
            year = special_witnesses[key]
        else:
            year = re.match(r".*([1-3][0-9]{3})", str(key))
            if year is not None:
                year = year.group(1)
                
        normalized_year = (int(year) - min_range) / (max_range - min_range) #range(1700, 2020), normalized to be between 0 and 1
        witness_score[key] = value * normalized_year
    return witness_score