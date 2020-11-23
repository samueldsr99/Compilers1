"""
Parsing Section
"""
import streamlit as st

import utils.grammar_processing as gp
from utils.parser import isLL1, metodo_predictivo_no_recursivo
from utils.render import LL1_to_dataframe
from utils.tokenizer import tokenize


def parsing():
    options = [
        'LL(1)',
        'LR(1)',
        'LR(0)',
    ]
    parser_algorithm = st.selectbox('Algoritmo de Parsing', options)

    if parser_algorithm == 'LL(1)':
        parser_LL1()
    if parser_algorithm == '':
        pass


def parser_LL1():
    result = gp.load_grammar()
    if result[0]:
        st.error('No se ha definido una gramatica\
            o la gramatica definida no es correcta')
    else:
        G = result[1]
        st.title('Parser LL(1)')

        if not isLL1(G):
            st.error('La gramática definida no es LL(1)\
                , no se puede aplicar este algoritmo de parsing')
        else:
            st.subheader('Tabla')
            frame = LL1_to_dataframe(G)
            st.write(frame)

            w = st.text_input("Inserte la cadena a parsear")

            if st.button("Parse"):
                parser = metodo_predictivo_no_recursivo(G)

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
