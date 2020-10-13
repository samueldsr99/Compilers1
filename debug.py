"""
For debug & testing
"""
import pandas as pd

from utils import grammar_processing as gp
from utils.first_follow import compute_firsts, compute_follows

# Testing First & Follows
G = gp.load_grammar()[1]

firsts = compute_firsts(G)
follows = compute_follows(G, firsts)

print('Firsts:')
for item in firsts.items():
    print(item)

print('Follows:')
for item in follows.items():
    print(item)
