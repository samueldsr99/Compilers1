"""
Parsing Section
"""
import streamlit as st

import utils.grammar_processing as gp
from utils.derivation_tree import LLDerivationTree, LRDerivationTree
from utils.parser import (
    isLL1,
    metodo_predictivo_no_recursivo,
    build_parsing_table,
    get_ll1_conflict
)
from utils.conflicts.ll_conflict import generate_ll1_conflict_string
from utils.conflicts.lr_conflict import generate_lr_conflict_string
from utils.render import LL1_to_dataframe, LR_table_to_dataframe
from utils.tokenizer import tokenize
from utils.Parsers.parserSR import (
    SHIFT_REDUCE,
    REDUCE_REDUCE,
)
from utils.Parsers.parserLR1 import LR1Parser, build_LR1_automaton
from utils.Parsers.parserSLR1 import SLR1Parser, build_LR0_automaton
from utils.Parsers.parserLALR1 import LALR1Parser, build_LALR1_automaton


def render_parser(G, algorithm: str, parser, is_ll1=False):
    """
    Render Parser Subsection
    """
    st.title('Parsear Cadena')
    w = st.text_input("Inserte la cadena a parsear")

    if st.button("comenzar"):
        st.subheader(f'Aplicando: {algorithm}')

        tokens = tokenize(G, w)

        if isinstance(tokens, list):
            productions = parser(tokens)
            if not productions:
                st.error("Error en parsing.\
                    La cadena no pertenece al lenguaje.")
            else:
                st.success("OK")
                if is_ll1:
                    tree = LLDerivationTree(productions)
                else:
                    tree = LRDerivationTree(productions)
                st.graphviz_chart(str(tree.graph()))
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

    options = [
        'Tabla de Parsing',
        'Parsear Cadena'
    ]

    M = build_parsing_table(G)

    if not isLL1(G, M):
        st.error('La gramática definida no es LL(1)')
        options.remove('Parsear Cadena')
        
        # Get conflicts
        pair = get_ll1_conflict(M)
        c1, c2 = M[pair[0], pair[1]][:2]
        st.subheader('Producciones de conflicto:')
        st.code(f'{c1}\n{c2}')

        s1, s2 = generate_ll1_conflict_string(G, M, pair)
        st.subheader('Cadenas de conflicto')
        st.code(f'{s1}\n{s2}')

    selected = st.multiselect('', options)

    if options[0] in selected:
        st.title('Tabla LL(1)')
        frame = LL1_to_dataframe(G)
        st.write(frame)
    if len(options) > 1 and options[1] in selected:
        parser = metodo_predictivo_no_recursivo(G)
        render_parser(G, 'método predictivo no recursivo', parser, is_ll1=True)


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

    options = [
        'Tabla de parsing',
        'Autómata LR1',
        'Parsear cadena'
    ]

    G = result[1]
    
    lr1_parser = LR1Parser(G)
    
    if len(lr1_parser.conflicts) > 0:
        options.remove('Parsear cadena')

        if lr1_parser.conflicts[0].type == SHIFT_REDUCE:
            st.error('La gramática definida tiene conflictos\
                Shift-Reduce')
        if lr1_parser.conflicts[0].type == REDUCE_REDUCE:
            st.error('La gramática definida tiene conflictos\
                Reduce-Reduce')

        for conf in lr1_parser.conflicts:
            st.code(f'{conf.value[0]}\n{conf.value[1]}')
        
        # TODO Report conflict string...
        r1, r2 = generate_lr_conflict_string(G, lr1_parser)
        st.subheader('Cadenas de conflicto:')
        st.code(f'{r1}\n{r2}')

    selected = st.multiselect('', options)

    if 'Tabla de parsing' in selected:
        lr1_parser._build_parsing_table()
        goto = LR_table_to_dataframe(lr1_parser.goto)
        action = LR_table_to_dataframe(lr1_parser.action)
        st.title('GOTO')
        st.write(goto)
        st.title('Action')
        st.write(action)
    if 'Autómata LR1' in selected:
        st.title('Automata LR(1)')
        automaton = build_LR1_automaton(lr1_parser.G.AugmentedGrammar(True))
        st.graphviz_chart(str(automaton.graph()))
    if 'Parsear cadena' in selected:
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

    options = [
        'Tabla de parsing',
        'Autómata LR0',
        'Parsear cadena'
    ]

    G = result[1]

    slr1_parser = SLR1Parser(G)
    if len(slr1_parser.conflicts) > 0:
        options.remove('Parsear cadena')

        if slr1_parser.conflicts[0].type == SHIFT_REDUCE:
            st.error('La gramática definida tiene conflictos\
                Shift-Reduce')
        if slr1_parser.conflicts[0].type == REDUCE_REDUCE:
            st.error('La gramática definida tiene conflictos\
                Reduce-Reduce')

        for conf in slr1_parser.conflicts:
            st.code(f'{conf.value[0]}\n{conf.value[1]}')
        
        # TODO Report conflict string...
        r1, r2 = generate_lr_conflict_string(G, slr1_parser)
        st.subheader('Cadenas de conflicto:')
        st.code(f'{r1}\n{r2}')


    selected = st.multiselect('', options)

    if 'Tabla de parsing' in selected:
        slr1_parser._build_parsing_table()
        goto = LR_table_to_dataframe(slr1_parser.goto)
        action = LR_table_to_dataframe(slr1_parser.action)
        st.title('GOTO')
        st.write(goto)
        st.title('Action')
        st.write(action)
    if 'Autómata LR0' in selected:
        st.title('Automata LR(0)')
        automaton = build_LR0_automaton(slr1_parser.G.AugmentedGrammar(True))
        st.graphviz_chart(str(automaton.graph()))
    if 'Parsear cadena' in selected:
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

    options = [
        'Tabla de parsing',
        'Autómata LALR(1)',
        'Parsear cadena'
    ]

    G = result[1]

    lalr1_parser = LALR1Parser(G)

    if len(lalr1_parser.conflicts) > 0:
        options.remove('Parsear cadena')

        if lalr1_parser.conflicts[0].type == SHIFT_REDUCE:
            st.error('La gramática definida tiene conflictos\
                Shift-Reduce')
        if lalr1_parser.conflicts[0].type == REDUCE_REDUCE:
            st.error('La gramática definida tiene conflictos\
                Reduce-Reduce')

        for conf in lalr1_parser.conflicts:
            st.code(f'{conf.value[0]}\n{conf.value[1]}')
        
        # TODO Report conflict string...
        r1, r2 = generate_lr_conflict_string(G, lalr1_parser)
        st.subheader('Cadenas de conflicto:')
        st.code(f'{r1}\n{r2}')

    selected = st.multiselect('', options)

    if 'Tabla de parsing' in selected:
        lalr1_parser._build_parsing_table()
        goto = LR_table_to_dataframe(lalr1_parser.goto)
        action = LR_table_to_dataframe(lalr1_parser.action)
        st.title('GOTO')
        st.write(goto)
        st.title('Action')
        st.write(action)
    if 'Autómata LALR(1)' in selected:
        st.title('Automata LR(0)')
        automaton = build_LALR1_automaton(lalr1_parser.G.AugmentedGrammar(True))
        st.graphviz_chart(str(automaton.graph()))
    if 'Parsear cadena' in selected:
        render_parser(G, 'método LALR(1)', lalr1_parser)
