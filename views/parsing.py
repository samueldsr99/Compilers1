"""
Parsing Section
"""
import streamlit as st

import utils.grammar_processing as gp
from utils.parser import isLL1, metodo_predictivo_no_recursivo
from utils.render import LL1_to_dataframe, LR_table_to_dataframe
from utils.tokenizer import tokenize
from utils.Parsers.parserLR1 import LR1Parser, build_LR1_automaton
from utils.Parsers.parserSLR1 import SLR1Parser, build_LR0_automaton
from utils.Parsers.parserLALR1 import LALRParser, build_lalr_automaton


def render_parser(G, algorithm: str, parser):
    """
    Render Parser Subsection
    """
    st.title('Parsear Cadena')
    w = st.text_input("Inserte la cadena a parsear")

    if st.button("comenzar"):
        st.subheader(f'Aplicando: {algorithm}')

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
                    st.text(f'{production.Left} -> {production.Right}')
        else:
            st.error("Error en tokenize: " + tokens)


def parsing():
    wrapper = {
        'LL(1)': parser_LL1,
        'LR(1)': parser_LR1,
        'SLR(1)': parser_SLR1,
        'LALR(1)': parser_LALR1
    }

    option = st.selectbox('Algoritmo de Parsing', list(wrapper.keys()))

    wrapper[option]()


def parser_LL1():
    """
    LL(1) Subsection
    """
    st.title('Parser LL(1)')

    result = gp.load_grammar()
    if result[0]:
        st.error('No se ha definido una gramatica\
            o la gramatica definida no es correcta')
        return

    G = result[1]

    if not isLL1(G):
        st.error('La gramática definida no es LL(1)\
            , no se puede aplicar este algoritmo de parsing')
        return

    options = [
        'Tabla de Parsing',
        'Parsear Cadena'
    ]

    selected = st.multiselect('', options)

    if options[0] in selected:
        st.title('Tabla LL(1)')
        frame = LL1_to_dataframe(G)
        st.write(frame)
    if options[1] in selected:
        parser = metodo_predictivo_no_recursivo(G)
        render_parser(G, 'método predictivo no recursivo', parser)


def parser_LR1():
    """
    LR(1) Subsection
    """
    st.title('Parser LR(1)')

    result = gp.load_grammar()
    if result[0]:
        st.error('No se ha definido una gramática\
            o la gramática definida no es correcta')
        return

    G = result[1]
    try:
        lr1_parser = LR1Parser(G)
    except Exception:
        st.error('La gramática definida tiene conflictos\
            Shift-Reduce o Reduce-Reduce')
        return

    options = [
        'Tabla de parsing',
        'Autómata LR1',
        'Parsear cadena'
    ]

    selected = st.multiselect('', options)

    if options[0] in selected:
        lr1_parser._build_parsing_table()
        goto = LR_table_to_dataframe(lr1_parser.goto)
        action = LR_table_to_dataframe(lr1_parser.action)
        st.title('GOTO')
        st.write(goto)
        st.title('Action')
        st.write(action)
    if options[1] in selected:
        st.title('Automata LR(1)')
        automaton = build_LR1_automaton(lr1_parser.G.AugmentedGrammar(True))
        st.graphviz_chart(str(automaton.graph()))
    if options[2] in selected:
        render_parser(G, 'método LR(1)', lr1_parser)


def parser_SLR1():
    """
    SLR(1) Subsection
    """
    st.title('Parser SLR(1)')

    result = gp.load_grammar()
    if result[0]:
        st.error('No se ha definido una gramatica\
            o la gramatica definida no es correcta')
        return

    G = result[1]
    try:
        slr1_parser = SLR1Parser(G)
    except Exception:
        st.error('La gramática definida tiene conflictos\
            Shift-Reduce o Reduce-Reduce')
        return

    options = [
        'Tabla de parsing',
        'Autómata LR0',
        'Parsear cadena'
    ]

    selected = st.multiselect('', options)

    if options[0] in selected:
        slr1_parser._build_parsing_table()
        goto = LR_table_to_dataframe(slr1_parser.goto)
        action = LR_table_to_dataframe(slr1_parser.action)
        st.title('GOTO')
        st.write(goto)
        st.title('Action')
        st.write(action)
    if options[1] in selected:
        st.title('Automata LR(0)')
        automaton = build_LR0_automaton(slr1_parser.G.AugmentedGrammar(True))
        st.graphviz_chart(str(automaton.graph()))
    if options[2] in selected:
        render_parser(G, 'método SLR(1)', slr1_parser)


def parser_LALR1():
    """
    LALR(1) Subsection
    """
    st.title('Parser LALR(1)')

    result = gp.load_grammar()
    if result[0]:
        st.error('No se ha definido una gramatica\
            o la gramatica definida no es correcta')
        return

    G = result[1]
    lalr1_parser = LALRParser(G)
    # try:
    #     lalr1_parser = LALRParser(G)
    # except Exception:
    #     st.error('La gramática definida tiene conflictos\
    #         Shift-Reduce o Reduce-Reduce')
        # return

    options = [
        'Tabla de parsing',
        'Autómata LALR(1)',
        'Parsear cadena'
    ]

    selected = st.multiselect('', options)

    if options[0] in selected:
        lalr1_parser._build_parsing_table()
        goto = LR_table_to_dataframe(lalr1_parser.goto)
        action = LR_table_to_dataframe(lalr1_parser.action)
        st.title('GOTO')
        st.write(goto)
        st.title('Action')
        st.write(action)
    if options[1] in selected:
        st.title('Automata LR(0)')
        automaton = build_lalr_automaton(lalr1_parser.G.AugmentedGrammar(True))
        st.graphviz_chart(str(automaton.graph()))
    if options[2] in selected:
        render_parser(G, 'método LALR(1)', lalr1_parser)
