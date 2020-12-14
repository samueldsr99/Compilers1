"""
Find for a conflict string on LL(1) Grammars
"""
from collections import deque
from cmp.pycompiler import Sentence, Production


def fill_sentences_dict(G):
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


def fill_fixed_sentences_dict(G, t, sentence_forms):
    fixed_sentences = {t: Sentence(t)}

    change = True
    while change:
        n = len(fixed_sentences)
        for production in G.Productions:
            left, right = production

            if left in fixed_sentences:
                continue

            if not right.IsEpsilon and right[0] in fixed_sentences:
                fixed_sentences[left] = \
                Sentence(
                    *([fixed_sentences[right[0]]] + [sentence_forms[symbol] for symbol in right[1:]])
                )

        change = n != len(fixed_sentences)

    return fixed_sentences


def get_path(G, x):
    pending = deque([x])
    ret = {x: Sentence(x)}

    productions = set(G.Productions)
    while pending:
        current = pending.popleft()

        visited = set()
        for production in productions:

            head, body = production

            if head in ret:
                continue

            sentence = Sentence()
            current_belong = False
            for i, symbol in enumerate(body):
                if symbol == current:
                    current_belong = True
                    sentence += ret[current]
                else:
                    sentence += symbol

            if current_belong:
                pending.append(head)
                ret[head] = sentence
                visited.add(production)

        productions -= visited

    return ret[G.startSymbol]


def generate_ll1_conflict_string(G, table, pair):
    left, right = pair

    c1, c2 = table[left, right][:2]

    sentence = get_path(G, left)
    sentence_forms = fill_sentences_dict(G)
    fixed_sentence = fill_fixed_sentences_dict(G, right, sentence_forms)

    i = tuple(sentence).index(left)

    x1 = c1.Right[0]
    x2 = c2.Right[0]

    str1 = Sentence(*(sentence[:i] + tuple(c1.Right) + sentence[i + 1:]))
    str2 = Sentence(*(sentence[:i] + tuple(c2.Right) + sentence[i + 1:]))

    ret1 = Sentence()
    for symbol in str1:
        if symbol == x1:
            ret1 += fixed_sentence[symbol]
        else:
            ret1 += sentence_forms[symbol]

    ret2 = Sentence()
    for symbol in str2:
        if symbol == x2:
            ret2 += fixed_sentence[symbol]
        else:
            ret2 += sentence_forms[symbol]
    
    return ret1, ret2
