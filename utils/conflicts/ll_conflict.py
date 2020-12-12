"""
Find for a conflict string on LL(1) Grammars
"""
from collections import deque
from cmp.pycompiler import Sentence, Production


def compute_sentence(G):
    """
    For each non terminal 'X' in the Grammar G compute a sentence of terminals 'S' where X ->* S
    """
    sentence = {t: Sentence(t) for t in G.terminals}

    change = True
    while change:
        n = len(sentence)
        for production in G.Productions:
            head, body = production

            if head in sentence:
                continue

            if body.IsEpsilon or all(symbol in sentence for symbol in body):
                sentence[head] = Sentence(*[sentence[symbol] for symbol in body])

        change = n != len(sentence)

    return sentence


def compute_fixxed_sentence(G, t, sentence_forms):
    """
    For each non terminal 'X' in the Grammar G compute a sentence of terminals that start with t 'tS'
    where X ->* tS
    """
    fixxed_sentence = {t: Sentence(t)}

    change = True
    while change:
        n = len(fixxed_sentence)
        for production in G.Productions:
            head, body = production

            if head in fixxed_sentence:
                continue

            if not body.IsEpsilon and body[0] in fixxed_sentence:
                fixxed_sentence[head] = Sentence(
                    *([fixxed_sentence[body[0]]] + [sentence_forms[symbol] for symbol in body[1:]]))

        change = n != len(fixxed_sentence)

    return fixxed_sentence


def shortest_production_path(G, x):
    """
    Compute the shortest poduction path from start symbol of
    Grammar G to a sentence form thad Contains the Non Temrinal X
    """
    queue = deque([x])
    sentence_form = {x: Sentence(x)}
    production_path = {x: [Production(x, Sentence(x))]}  # Eliminar esta linea de testeo

    productions = set(G.Productions)
    while queue:
        current = queue.popleft()

        visited_productions = set()
        for production in productions:

            head, body = production

            if head in sentence_form:
                continue

            sentence = Sentence()
            current_belong = False
            for i, symbol in enumerate(body):
                if symbol == current:
                    current_belong = True
                    sentence += sentence_form[current]
                else:
                    sentence += symbol

            if current_belong:
                queue.append(head)
                sentence_form[head] = sentence
                production_path[head] = [production] + production_path[current]
                visited_productions.add(production)

        productions -= visited_productions

    assert G.startSymbol in sentence_form, f'{x} is not reacheable from start symbol {G.startSymbol}'

    return sentence_form[G.startSymbol], production_path[G.startSymbol][:-1]


def generate_ll1_conflict_string(G, table, pair):
    """
    Generates conflict string given a parser and it's
    conflict nonterminal-terminal pair
    """
    left, right = pair

    c1, c2 = table[left, right][:2]

    sentence, _ = shortest_production_path(G, left)
    sentence_forms = compute_sentence(G)
    sentence_forms_fixxed = compute_fixxed_sentence(G, right, sentence_forms)

    i = tuple(sentence).index(left)

    x1 = c1.Right[0]
    x2 = c2.Right[0]

    s1 = Sentence(*(sentence[:i] + tuple(c1.Right) + sentence[i + 1:]))
    s2 = Sentence(*(sentence[:i] + tuple(c2.Right) + sentence[i + 1:]))

    ss1 = Sentence()
    for symbol in s1:
        if symbol == x1:
            ss1 += sentence_forms_fixxed[symbol]
        else:
            ss1 += sentence_forms[symbol]

    ss2 = Sentence()
    for symbol in s2:
        if symbol == x2:
            ss2 += sentence_forms_fixxed[symbol]
        else:
            ss2 += sentence_forms[symbol]
    
    return ss1, ss2
