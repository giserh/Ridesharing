"""
Draw a graph with matplotlib, color by degree.

You must have matplotlib for this to work.
"""
__author__ = """Sol Ma (sma21@uic.edu)"""
import matplotlib.pyplot as plt
    
import networkx as nx

def drawRelation(relation):
    G=nx.DiGraph()
    G.add_edges_from(relation)
    nx.draw(G)
    plt.show()