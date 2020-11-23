"""
Grammar Details Section
"""
import streamlit as st

import utils.grammar_processing as gp
from utils.grammar_cleaner import (GrammarPipeline, remove_ambiguity,
                                   remove_epsilon, remove_left_recursion,
                                   remove_unit, remove_unreachable,
                                   remove_vars_nothing)
from utils.parser import isLL1


def render_grammar(G, name='G'):
    st.subheader('No terminales:')
    st.text(str(G.nonTerminals))
    st.subheader('Terminales:')
    st.text('\t' + str(G.terminals))
    st.subheader('Producciones:\n')
    for i in G.Productions:
        left = i.Left
        right = 'epsilon' if i.IsEpsilon else i.Right
        st.text(str(left) + " -> " + str(right))


def grammar_details():
    result = gp.load_grammar()
    if result[0]:
        st.error('No se ha definido una gramatica\
             o la gramatica definida no es correcta')
        st.error('Errors: ' + str(result[1]))
    else:
        G = result[1]

        st.header('Detalles de la gramatica:')
        render_grammar(G, 'G')

        lr_result = gp.has_left_recursion(G)
        if lr_result:
            st.warning('La gramática tiene recursión izquierda:\
                 {} -> {}'.format(lr_result.Left, lr_result.Right))
        elif (not isLL1(G)):
            st.warning('La gramática no es LL(1)')
        else:
            st.success('La gramática es LL(1)')

        new_G = G.copy()
        GrammarPipeline(new_G, [
            remove_epsilon,
            remove_unit,
            remove_vars_nothing,
            remove_unreachable,
            remove_left_recursion,
            remove_ambiguity,
        ]).run()
        st.header('Gramática transformada\
        (sin recursión izquierda inmediata, prefijos comunes\
        y producciones innecesarias)')
        render_grammar(new_G, "G'")
        if isLL1(new_G):
            st.success('La gramática transformada es LL(1).')
        else:
            st.error('La gramática transformada tampoco es LL(1).')
