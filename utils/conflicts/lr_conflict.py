"""
Find for a conflict string on LR Grammars
"""
from collections import deque
from sys import exit

from cmp.automata import State
from cmp.pycompiler import Sentence
from utils.first_follow import (
    compute_firsts,
    compute_follows
)
from utils.Parsers.parserLR1 import build_LR1_automaton


def path_from(s):
    pending = deque([s])

    parents = {s: None}
    visited = set()
    visited.add(s)

    while pending:
        current = pending.popleft()
        print('~' * 160)
        print(f'current: {current.state}')
        print('~' * 160)
        # input()

        # if current in visited:
        #     continue

        # visited.add(current)

        for symbol in current.transitions:
            dest = current.get(symbol)
            if not dest in visited:
                print(f'with symbol: {symbol}')
                print(f'dest: {dest}')
                pending.append(dest)
                parents[dest] = current, symbol
                visited.add(dest)
        print('_' * 160)

    return parents


def path_from_to(source, dest):
    parents = path_from(source)
    print(f'source: {source}')

    path = [dest]
    s = dest
    while parents[s] is not None:
        s, symbol = parents[s]
        print(s)
        print(symbol)
        input()
        path += [symbol, s]
    path.reverse()
    print('Finished')
    print(f'path: {path}')
    input()
    return path


def move(s, guide_sentence):
    path = []
    node = s
    for symbol in guide_sentence:
        path += [node, symbol]
        node = node.get(symbol.Name)
    path.append(node)

    return path


def reduce_production(s, p, state_list, lookahead):
    states = {s}
    print("+++++++++++++++++++++++++++")
    print(s)
    print(p)
    print(state_list)
    print(lookahead)

    stack = list(p.Right)

    while stack:
        symbol = stack.pop()

        next_states = set()
        for s in state_list:
            if s.has_transition(symbol.Name) and s.get(symbol.Name) in states:
                next_states.add(s)
        states = next_states
    reduced_state = states.pop()

    path = move(reduced_state, p.Right)
    path.append(lookahead)
    return path


def sentence_path(init, conflict_state, symbol, p):
    """
    Computes the path from init automaton state to 'conflict_state' passing
    through state reduced from 'conflict_state' by production 'p'
    """
    states = [s for s in init]
    rpath = reduce_production(conflict_state, p, states, symbol)
    print('rpath')
    for p in rpath:
        print(p)
    input()
    lpath = path_from_to(init, rpath[0])
    return lpath + rpath[1:]


def expand_path(init, path, follows):
    """
    Expand the non terminal symbols in the given path until all becomes in terminals
    and return a sentence with these sequenced terminals
    """
    i = -2
    table = {s: set(s.state) for s in init}

    lookahead = path[-1]
    while i >= -len(path):
        current = path[i]
        symbol = path[i + 1]
        print('expanding path')
        print(i)
        print(current)
        print(symbol)
        input()

        if symbol.IsTerminal:
            lookahead = symbol
            i -= 2
            continue

        reductors = [item for item in current.state if item.production.Left == current and item in table[current]]
        
        for item in current.state:
            print(f'item: {item}')
            print(f'table[current]: {table[current]}')
            print(f'item.production.Left: {item.production.Left}, type: {type(item.production.Left)}')
            print(f'type current: {type(current)}')
            print(f'item in table: {item in table[current]}')


        print(f'reductors: {reductors}')
        input()

        while reductors:
            reductor = reductors.pop()            

            subpath = move(current, reductor.production.Right)

            print(f'reductor: {reductor}')
            print(f'subpath: {subpath}')
            input()

            last = subpath.pop()
            ritem = [item for item in last.state if item.IsReduceItem and item.production == reductor.production][0]
            lookaheads = follows[ritem.Left] if not ritem.lookaheads else ritem.lookaheads

            if lookahead in lookaheads:
                table[current].remove(reductor)
                path = path[:i] + subpath + path[i + 2:]
                break

    return Sentence(*[s for s in path if not isinstance(s, State)])


def generate_lr_conflict_string(G, parser):
    automaton = build_LR1_automaton(G.AugmentedGrammar(True))
    states = {}

    for it, node in enumerate(automaton):
        states[it] = node

    # for conf in parser.conflicts:
    #     print(f'conf.key {conf.key}, conf.value {conf.value}')
    #     if conf.value[0][0] == 'REDUCE':
    #         st, symbol = conf.key
    #         production = conf.value[0][1]
    #         print(states[st])
    #     if conf.value[1][0] == 'REDUCE':
    #         st, symbol = conf.key
    #         production = conf.value[1][1]
    #         print(states[st])
    
    st, symbol = parser.conflicts.key
    _, production = parser.action[st, symbol].pop()
    print(f'state: {st}')
    print(f'symbol: {symbol}')

    assert (st is not None and production is not None and symbol is not None)

    print(production)
    input()
    path = sentence_path(automaton, states[st], symbol, production)

    for p in path:
        print(f'path: {p}')
    input()

    firsts = compute_firsts(G)
    follows = compute_follows(G, firsts)

    extended = expand_path(automaton, path, follows)

    return extended
