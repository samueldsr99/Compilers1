import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import pandas as pd

# utils
from utils import grammar_processing as gp
from utils.first_follow import compute_firsts, compute_follows
from utils.parser import isLL1, build_parsing_table, metodo_predictivo_no_recursivo
from utils.grammar_cleaner import remove_left_recursion, remove_epsilon, remove_unit, remove_vars_nothing, remove_unreachable, remove_ambiguity
from utils.grammar_cleaner import GrammarPipeline
from utils.tokenizer import tokenize

st.title('Compilacion: Proyecto 1')

choices = [
    'Insertar Gramatica',
    'Detalles de la gramatica',
    'Calcular Firsts & Follows',
    'Parsear con método predictivo no recursivo',
]

def render_grammar(G, name='G'):
    st.subheader('No terminales:')
    st.text(str(G.nonTerminals))
    st.subheader('Terminales:')
    st.text('\t' + str(G.terminals))
    st.subheader('Producciones:\n')
    for i in G.Productions:
        st.text(str(i.Left) + " -> " + str(i.Right))

choice = st.sidebar.radio('Seleccione una opcion:', choices)

# Insertar gramatica
if choice == choices[0]:
    initial = st.text_area('Inserte el no terminal inicial')
    terminals = st.text_area('Inserte los terminales separados por espacio')
    non_terminals = st.text_area('Inserte los no terminales separados por espacio (incluyendo el no terminal inicial)')
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

# Detalles de la gramatica
elif choice == choices[1]:
    result = gp.load_grammar()
    if result[0]:
        st.error('No se ha definido una gramatica o la gramatica definida no es correcta')
        st.error('Errors: ' + str(result[1]))
    else:
        G = result[1]

        st.header('Detalles de la gramatica:')
        render_grammar(G, 'G')

        lr_result = gp.has_left_recursion(G)
        if lr_result:
            st.warning('La gramática tiene recursión izquierda: {} -> {}'.format(lr_result.Left, lr_result.Right))
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
        st.header('Gramática transformada:')
        render_grammar(new_G, "G'")

# Calcular Firsts & Follows
elif choice == choices[2]:
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

# Parsear con metodo predictivo no recursivo
elif choice == choices[3]:
    result = gp.load_grammar()
    if result[0]:
        st.error('No se ha definido una gramatica o la gramatica definida no es correcta')
        st.error('Errors: ' + str(result[1]))
    else:
        G = result[1]

        if not isLL1(G):
            st.error('La grámatica definida no es LL(1), no se puede aplicar este algoritmo de parsing')
        else:        
            firsts = compute_firsts(G)
            follows = compute_follows(G, firsts)
            M = build_parsing_table(G, firsts, follows)
            
            rows, columns = set(), set()
            matrix = []

            for item in M:
                rows.add(item[0])
                columns.add(item[1])
            
            for row in rows:
                matrix.append([])
                for column in columns:
                    try:
                        production = M[row, column][0]
                        matrix[-1].append(str(production.Left) + ' -> ' + str(production.Right))
                    except KeyError:
                        matrix[-1].append(' ')

            st.subheader('Tabla de parsing')

            frame = pd.DataFrame(matrix, index=rows, columns=columns)
            st.write(frame)

            # Parsing
            st.subheader("Inserte la cadena a parsear")
            w = st.text_area('')
            
            if st.button("Parsear"):
                parser = metodo_predictivo_no_recursivo(G, M)

                tokens = tokenize(G, w)
                
                if isinstance(tokens, list):
                    left_parse = parser(tokens)
                    if not left_parse:
                        st.error("Error en parsing. La cadena no pertenece al lenguaje.")
                    else:
                        st.success("OK")
                        st.subheader("Producciones a aplicar:")
                        for production in left_parse:
                            st.text(str(production.Left) + " -> " + str(production.Right))
                else:
                    st.error("Error en tokenize: " + tokens)
