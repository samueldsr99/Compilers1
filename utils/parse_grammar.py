"""
Utils for parsing grammars from plain text to CP format

format in input
initial: UpperCase letter
terminals: LowerCase letters separated by commas
non_terminals: UpperCase letters separated by commas
productions: Terminal -> non_terminals
    example: A -> b
"""

# Grammar modules
from cmp.pycompiler import Symbol
from cmp.pycompiler import NonTerminal
from cmp.pycompiler import Terminal
from cmp.pycompiler import EOF
from cmp.pycompiler import Sentence, SentenceList
from cmp.pycompiler import Epsilon
from cmp.pycompiler import Production
from cmp.pycompiler import Grammar
from cmp.utils import pprint, inspect

# Debug
import streamlit as st

f = {}
errors = []

def parse_grammar(initial, terminals, non_terminals, productions):
    """
    Parse grammar from plain text to CP format
    """
    G = Grammar()
    productions = productions.split('\n')
    f['epsilon'] = G.Epsilon
    f['EOF'] = G.EOF
    f[initial] = G.NonTerminal(initial, True)
    
    for terminal in terminals.split(' '):
        f[terminal] = G.Terminal(terminal)
    
    for non_terminal in non_terminals.split(' '):
        if non_terminal != f[initial].Name:
            f[non_terminal] = G.NonTerminal(non_terminal)
    
    # Parsing productions
    for production in productions:
        if not production:
            continue
        parse_production(production, G)
        if errors:
            break
    
    if errors:
        return (-1, errors)
    
    return (0, G)

def parse_production(production, G):
    production = production.split(' ')
    match(production[0], 'id')
    match(production[1], '->')

    if errors:
        return
    
    left = f[production[0]]
    
    it = 2
    right = SentenceList()
    while it < len(production):
        s = Sentence()
        while it < len(production) and production[it] != '|':
            match(production[it], 'id')

            if errors:
                return
            
            if production[it] == 'epsilon':
                s = G.Epsilon
            else:
                s += f[production[it]]
            
            it += 1
        it += 1

        right.Add(s)
    
    left %= right

def tokenize(w):
    tokens = []
    for token in w:
        if f.get(token) and f[token].IsTerminal:
            tokens.append(f[token])
        else:
            return None
    
    tokens.append(f['EOF'])
    
    return tokens

def match(token, type):
    if type == 'id':
        if f.get(token) == None:
            errors.append('undefined id: ' + str(token))
    elif token != type:
        errors.append('expected: ' + str(type))