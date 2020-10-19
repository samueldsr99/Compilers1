"""
Simple tokenizer
"""
from utils.grammar_processing import normalize

def tokenize(G, w):
    """
    tokenize a string w based on Grammar non terminals
    """
    if not w:
        return [G.EOF]

    w = normalize(w)
    w = w[:-1].split(' ')
    
    f = G.symbDict

    tokens = []
    for token in w:
        if f.get(token) and f[token].IsTerminal:
            tokens.append(f[token])
        else:
            return "token no definido: " + token
    tokens.append(G.EOF)
    return tokens
