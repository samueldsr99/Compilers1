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
from utils.Parsers.parserLR1 import LR1Parser
from utils.conflicts.lr_conflict import generate_lr_conflict_string


G = gp.load_grammar()[1]

lr1_parser = LR1Parser(G)

assert len(lr1_parser.conflicts) > 0, "Grammar has no conflicts"

r1, r2 = generate_lr_conflict_string(G, lr1_parser)
st.subheader('Cadenas de conflicto:')
st.code(f'{r1}\n{r2}')
