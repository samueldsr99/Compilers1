"""
Utils for processing grammars
"""
from cmp.pycompiler import Grammar, NonTerminal, Terminal
from utils.NFA import NFA

from .parse_grammar import parse_grammar


def insert_grammar(initial, terminals, non_terminals, productions):
    """
    Insert grammar info and saves it in data folder to make persistent
    """

    out = open('data/grammar.txt', 'w')

    for i in [initial, terminals, non_terminals, productions]:
        out.write(i)

def load_grammar():
    """
    Load grammar info from data folder and parses it
    Returns tuple (output, grammar | errors)
        if output != 0: errors
        else: grammar
    Grammar is in CP format (CP -> Clase practica)
    """

    inp = open('data/grammar.txt', 'r')

    initial = inp.readline()[:-1]
    terminals = inp.readline()[:-1]
    non_terminals = inp.readline()[:-1]

    productions = ""

    line = inp.readline()
    while line:
        productions += line
        line = inp.readline()
    
    G = parse_grammar(initial, terminals, non_terminals, productions)

    return G

def has_left_recursion(G):
    """
    Check if Grammar has Left Recursion
    Returns production if True, None elsewhere
    """

    for nt in G.nonTerminals:
        for production in nt.productions:
            if not production.IsEpsilon and production.Left == production.Right[0]:
                return production

    return None

def normalize(s):
    """
    append \n from string
    """
    
    if s[-1] != '\n':
        s += '\n'
    
    return s

def is_regular(G: Grammar) -> bool:
    """
    Checks if grammar `G` is regular.
    """
    # Maybe can be ommited left part checking
    for prod in G.Productions:
        if prod.IsEpsilon:
            continue
        # this was made for debugging reasons
        if len(prod.Left) != 1:
            return False
        if type(prod.Left) is not NonTerminal:
            return False
        if len(prod.Right) not in (1, 2):
            return False
        if Terminal not in (type(sym) for sym in prod.Right):
            return False
        # if len(prod.Left) != 1 or type(prod.Left) is not NonTerminal or \
        # len(prod.Right) not in (1, 2) or Terminal not in (type(sym) for sym in prod.Right):
        #     print('here {}'.format(prod))
        #     return False
    return True

def grammar_to_dfa(G: Grammar):
    """
    Converts a regular grammar to a DFA.
    """
    assert is_regular(G), 'Grammar is not Regular'

    mapping = {nonTerm: value for nonTerm, value in zip(G.nonTerminals, range(len(G.nonTerminals)))}
    transitions = {}
    final = len(G.nonTerminals)
    for prod in G.Productions:
        if prod.IsEpsilon:
            symbol = ''
            go_state = final
        elif prod.Right[0].IsTerminal:
            symbol = prod.Right[0].Name
            if len(prod.Right) == 1:
                go_state = final
            else:
                go_state = mapping[prod.Right[1]]
        else:
            symbol = prod.Right[1].Name
            go_state = mapping[prod.Right[0]]
        try:
            transitions[(mapping[prod.Left], symbol)].append(go_state)
        except KeyError:
            transitions[(mapping[prod.Left], symbol)] = [go_state]
        # print(mapping[prod.Left], symbol, '->', go_state,)
    nfa = NFA(
        states=final + 1,
        finals=[final],
        transitions=transitions,
        start=mapping[G.startSymbol]
    )
    return nfa.to_dfa()
