"""
Utils for processing grammars
"""
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
    True is Grammar has Left Recursion
    """

    for nt in G.nonTerminals:
        if any(not production.IsEpsilon and production.Left == production.Right[0] for production in nt.productions):
            return True

    return False

def normalize(s):
    """
    append \n from string
    """
    
    if s[-1] != '\n':
        s += '\n'
    
    return s
