import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import pandas as pd
import os
import re

# utils
from utils import grammar_processing as gp
from utils.first_follow import compute_firsts, compute_follows
from utils.parser import isLL1, build_parsing_table, metodo_predictivo_no_recursivo
from utils.grammar_cleaner import remove_left_recursion, remove_epsilon, remove_unit, remove_vars_nothing, remove_unreachable, remove_ambiguity
from utils.grammar_cleaner import GrammarPipeline
from utils.tokenizer import tokenize
from utils.NFA import NFA


st.title('Compilacion: Proyecto 1')

choices = [
    'Insertar Gramatica',
    'Detalles de la gramatica',
    'Calcular Firsts & Follows',
    'Parsear con método predictivo no recursivo',
    'Visualizar autómata'
]


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


choice = st.sidebar.radio('Seleccione una opcion:', choices)

# Insertar gramatica
if choice == choices[0]:
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

# Detalles de la gramatica
elif choice == choices[1]:
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

# Calcular Firsts & Follows
elif choice == choices[2]:
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

# Parsear con metodo predictivo no recursivo
elif choice == choices[3]:
    result = gp.load_grammar()
    if result[0]:
        st.error('No se ha definido una gramatica\
             o la gramatica definida no es correcta')
        st.error('Errors: ' + str(result[1]))
    else:
        G = result[1]

        if not isLL1(G):
            st.error('La grámatica definida no es LL(1)\
                , no se puede aplicar este algoritmo de parsing')
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
                        matrix[-1].append(
                            str(production.Left) + ' -> ' +
                            str(production.Right)
                        )
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
                        st.error("Error en parsing.\
                            La cadena no pertenece al lenguaje.")
                    else:
                        st.success("OK")
                        st.subheader("Producciones a aplicar:")
                        for production in left_parse:
                            s = str(production.Left) + ' -> ' + \
                                str(production.Right)
                            st.text(s)
                else:
                    st.error("Error en tokenize: " + tokens)

# Visualizar autómata
elif choice == choices[4]:
    result = gp.load_grammar()
    if result[0]:
        st.error('No se ha definido una gramatica\
             o la gramatica definida no es correcta')
        st.error('Errors: ' + str(result[1]))
    elif not gp.is_regular(result[1]):
        st.error('La gramática definida no es regular.')
    else:
        G = result[1]

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

        st.subheader('Verificar expresión regular:')
        txt = st.text_area('')

        if st.button('Verificar'):
            match = re.fullmatch(regex, txt)
            if not match or match.end() != len(txt):
                st.error('El texto introducido no pertenece al lenguaje.')
            else:
                st.success('OK')
