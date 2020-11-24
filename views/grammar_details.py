"""
Grammar Details Section
"""
import os
import re

import streamlit as st

import utils.grammar_processing as gp
from utils.grammar_cleaner import (GrammarPipeline, remove_ambiguity,
                                   remove_epsilon, remove_left_recursion,
                                   remove_unit, remove_unreachable,
                                   remove_vars_nothing)
from utils.NFA import NFA


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


def render_regular_automaton(G):
    """
    Shows regular automaton for Grammar G
    """
    st.title('Autómata Regular')
    if not gp.is_regular(G):
        st.error('La gramática definida no es regular.')
        return

    dfa = gp.grammar_to_dfa(G)
    extended = NFA.extend_automaton(dfa)

    dfa.graph().write_png(os.path.join('data', 'dfa.png'))
    extended.graph().write_png(os.path.join('data', 'ext.png'))

    st.subheader('Autómata finito determinista obtenido de la gramática:')
    st.image(os.path.join('data', 'dfa.png'))

    st.subheader('Autómata extendido para hallar la expresión regular:')
    st.image(os.path.join('data', 'ext.png'))

    regex = extended.get_regex()

    st.subheader('Expresión regular:')
    st.text('{}'.format(regex))

    txt = st.text_input('Verificar expresión regular:')

    if st.button('Verificar'):
        match = re.fullmatch(regex, txt)
        if not match or match.end() != len(txt):
            st.error('La cadena no pertenece al lenguaje.')
        else:
            st.success('OK')


def grammar_details():
    result = gp.load_grammar()
    if result[0]:
        st.error('No se ha definido una gramatica\
             o la gramatica definida no es correcta')
        st.error('Errors: ' + str(result[1]))
        return

    G = result[1]

    st.header('Detalles de la gramatica:')

    options = [
        'Gramática',
        'Gramática simplificada',
    ]
    selected = st.selectbox('', options)

    if options[0] == selected:
        st.markdown('# Gramática original')
        render_grammar(G)
    elif options[1] == selected:
        st.markdown('# Gramática simplificada\n\
            * Sin recursión izquierda inmediata\n\
            * Sin producciones innecesarias\n\
            * Sin prefijos comunes')
        new_G = G.copy()
        pipeline = GrammarPipeline(new_G, [
            remove_epsilon,
            remove_unit,
            remove_vars_nothing,
            remove_unreachable,
            remove_left_recursion,
            remove_ambiguity
        ])

        pipeline.run()
        render_grammar(new_G)

    if options[0] == selected:
        lr_result = gp.has_left_recursion(G)
        if lr_result:
            st.warning('La gramática tiene recursión izquierda:\
                    {} -> {}'.format(lr_result.Left, lr_result.Right))

    if st.checkbox('Autómata Regular'):
        render_regular_automaton(G)
