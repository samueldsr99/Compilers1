"""
For debug & testing
"""
import pandas as pd

from utils import grammar_processing as gp
from utils.first_follow import compute_firsts, compute_follows
from utils.grammar_cleaner import (GrammarPipeline, remove_ambiguity,
                                   remove_epsilon, remove_left_recursion,
                                   remove_unit, remove_unreachable,
                                   remove_vars_nothing)
from utils.tokenizer import tokenize

G = gp.load_grammar()[1]

# print(tokenize(G, 'int + int * ( int * int + int )'))

# print('Before:')
# print(G)

# GrammarPipeline(G, [
#     remove_epsilon,
#     remove_unit,
#     remove_vars_nothing,
#     remove_unreachable,
#     remove_left_recursion,
#     remove_ambiguity,
# ]).run()

# print('After:')
# print(G)

# Testing automatons

import numpy as np
import pydot

from utils.DFA import DFA
from utils.NFA import NFA

# automaton = NFA(states=3, finals=[1], transitions={
#     (0, 'a'): [1],
#     (1, 'a'): [2],
#     (2, 'b'): [1],
#     (1, 'b'): [0]
# })
automaton = NFA(states=6, finals=[3, 5], transitions={
    (0, ''): [ 1, 2 ],
    (1, ''): [ 3 ],
    (1,'b'): [ 4 ],
    (2,'a'): [ 4 ],
    (3,'c'): [ 3 ],
    (4, ''): [ 5 ],
    (5,'d'): [ 5 ]
})

automaton.graph().write_png('automaton.png')

dfa = automaton.to_dfa()

dfa.graph().write_png('to_dfa.png')
print(automaton.finals)

new = NFA.extend_automaton(automaton)

new.graph().write_png('extended.png')

adj_list = {}
r_adj_list = {}
new._build_adj_list(adj_list, r_adj_list)

print('adj_list:', adj_list)
print('r_adj_list:', r_adj_list)

regex = new.to_regex()
print(regex)

# testing the regex obtained
import re

tests = [
    'bdddddd',
    'addddddddd',
    'a',
    'b',
    'c',
    'ccccc',
    '',
]
for t in tests:
    print(re.fullmatch(regex, t))
    assert re.fullmatch(regex, t).end() == len(t)
