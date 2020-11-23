"""
Insert Grammar Section
"""
import streamlit as st
import utils.grammar_processing as gp


def insert_grammar():
    initial = st.text_area('Inserte el no terminal inicial')
    terminals = st.text_area('Inserte los terminales separados por espacio')
    non_terminals = st.text_area('Inserte los no terminales separados por espacio\
         (incluyendo el no terminal inicial)')
    productions = st.text_area('Inserte las producciones de su gramatica')

    if st.button('Insertar gramatica'):
        # Basic parsing
        if initial and terminals and productions:
            initial = gp.normalize(initial)
            terminals = gp.normalize(terminals)
            non_terminals = gp.normalize(non_terminals)
            productions = gp.normalize(productions)

            gp.insert_grammar(initial, terminals, non_terminals, productions)
            st.success('Gramatica definida')
        else:
            st.error('Quedan parametros por definir')
