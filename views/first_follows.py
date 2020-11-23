"""
First & Follows Section
"""
import pandas as pd
import streamlit as st

import utils.grammar_processing as gp
from utils.first_follow import compute_firsts, compute_follows


def first_follows():
    result = gp.load_grammar()
    if result[0]:
        st.error('No se ha definido una gramatica\
             o la gramatica definida no es correcta')
        st.error('Errors: ' + str(result[1]))
    else:
        G = result[1]

        firsts = compute_firsts(G)
        follows = compute_follows(G, firsts)

        st.subheader('Firsts:')

        st.write(pd.DataFrame({
            'keys': firsts.keys(),
            'values': firsts.values()
        }))

        st.subheader('Follows:')

        st.write(pd.DataFrame({
            'keys': follows.keys(),
            'values': follows.values()
        }))
