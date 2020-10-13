import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import pandas as pd

# utils
from utils import grammar_processing as gp
from utils.first_follow import compute_firsts, compute_follows

st.title('Compilacion: Proyecto 1')

choices = [
    'Insertar Gramatica',
    'Detalles de la gramatica',
    'Calcular First & Follows',
    'Parsear con metodo predictivo no recursivo',
]

choice = st.sidebar.radio('Seleccione una opcion:', choices)

# Insertar gramatica
if choice == choices[0]:
    initial = st.text_area('Inserte el no terminal inicial')
    terminals = st.text_area('Inserte los terminales separados por espacio')
    non_terminals = st.text_area('Inserte los no terminales separados por espacio (No insertar el no terminal inicial)')
    productions = st.text_area('Inserte las producciones de su gramatica')

    if st.button('Insertar gramatica'):
        # Basic parsing
        if initial and terminals and non_terminals and productions:
            initial = gp.normalize(initial)
            terminals = gp.normalize(terminals)
            non_terminals = gp.normalize(non_terminals)
            productions = gp.normalize(productions)

            gp.insert_grammar(initial, terminals, non_terminals, productions)
            st.success('Gramatica definida')
        else:
            st.error('Quedan parametros por definir')

# Detalles de la gramatica
if choice == choices[1]:
    result = gp.load_grammar()
    if result[0]:
        st.error('No se ha definido una gramatica o la gramatica definida no es correcta')
        st.error('Errors: ' + str(result[1]))
    else:
        G = result[1]

        st.header('Detalles de la gramatica:')
        st.subheader('No terminales:')
        st.text(str(G.nonTerminals))
        st.subheader('Terminales:')
        st.text('\t' + str(G.terminals))
        st.subheader('Producciones:\n')
        for i in G.Productions:
            st.text(str(i.Left) + " -> " + str(i.Right))

if choice == choices[2]:
    result = gp.load_grammar()
    if result[0]:
        st.error('No se ha definido una gramatica o la gramatica definida no es correcta')
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

        # for item in firsts:
        #     st.text("{}: {}".format(str(item), str(firsts[item])))

        # st.subheader('Follows:')

        # for item in follows:
        #     st.text("{}: {}".format(str(item), str(follows[item])))
