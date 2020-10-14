"""
For debug & testing
"""
import pandas as pd

from utils import grammar_processing as gp
from utils.first_follow import compute_firsts, compute_follows
from utils.grammar_cleaner import remove_left_recursion, remove_epsilon, remove_unit, remove_vars_nothing, remove_unreachable, remove_ambiguity, GrammarPipeline
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

print(gp.has_left_recursion(G))
