"""

"""
import itertools as it

from cmp.pycompiler import Grammar, NonTerminal, Production, Sentence


def remove_epsilon(G: Grammar):
    """
    Removes e-productions from G.
    """ 
    prods = G.Productions
    
    # Find non terminals that derives in epsilon
    nullables = []
    changed = True
    while changed:
        changed = False
        for prod in prods:
            for symbol in prod.Right:
                if symbol in nullables:
                    continue
                elif not symbol.IsEpsilon:
                    break
            else:
                if prod.Left not in nullables:
                    nullables.append(prod.Left)
                    changed = True

    # Decomposing of productions removing one or multiple nullables non terminals
    
    # Removing old productions
    G.Productions = []
    for nt in G.nonTerminals:
        nt.productions = []
    
    # Adding new productions
    for prod in prods:
        prod_nullables = {
            index: symbol for index, symbol in zip(range(len(prod.Right)), prod.Right) \
            if symbol in nullables
        }
        for i in range(1, len(prod_nullables) + 1):              # Size iter
            for subset in it.combinations(prod_nullables, i):    # Subset iter
                right_part = []
                for j in range(len(prod.Right)):
                    if j not in subset:
                        right_part.append(prod.Right[j])
                if len(right_part) > 0:
                    new_prod = Production(prod.Left, Sentence(*right_part))
                else:
                    new_prod = Production(prod.Left, G.Epsilon)
                if new_prod not in G.Productions:
                    G.Add_Production(new_prod)
    
    # Adding old productions
    for prod in prods:
        G.Add_Production(prod)

    prods = G.Productions
    G.Productions = []
    useless_symbols = [symbol for symbol in nullables if all(prod.IsEpsilon for prod in symbol.productions)]
    # Removing productions that contains non terminals that derive in epsilon
    for prod in prods:
        if prod.IsEpsilon or any(symbol in useless_symbols for symbol in prod.Right):
            continue
        else:
            G.Add_Production(prod)

    # Removing non terminals symbols with no productions
    for s in useless_symbols:
        G.nonTerminals.remove(s)
        G.symbDict.pop(s.Name)


def remove_unit(G: Grammar):
    """
    Removes unit productions from G.
    Additionally this removes cycles.
    """
    def is_unit(p: Production) -> bool:
        """
        True if production have the form A -> B
        """
        return len(p.Right) == 1 and p.Right[0].IsNonTerminal

    prods = [prod for prod in G.Productions]

    unit_prods = [p for p in prods if is_unit(p)]
    variables = {p.Left.Name: {p.Right[0].Name} for p in unit_prods}

    change = True
    while change:
        change = False
        for v in variables:
            l = len(variables[v])
            iter_set = {s for s in variables[v]}
            for s in iter_set:
                if s == v:      # Do not check own set of a variable
                    continue
                try:
                    for x in variables[s]:
                        if v != x:          # Avoids add a key to his set
                            variables[v].add(x)
                except KeyError:    # Reached a symbol that belongs to right part of an unit prod
                    pass            # that is not in variables' keys (is not left part of a unit prod)
            if l != len(variables[v]):
                change = True
    # for x in variables.items():
    #     print(x)
    
    for v in variables:
        for s in variables[v]:
            for p in G[s].productions:
                if not is_unit(p):
                    prods.append(Production(G[v], p.Right))

    # Replace old productions by new productions
    # Don't add unit productions
    G.Productions = []          # Clean grammar productions
    for nt in G.nonTerminals:   # Clean non terminals productions
        nt.productions = []
    for p in prods:             # Add new productions
        if not is_unit(p):
            G.Add_Production(p)


def remove_vars_nothing(G: Grammar):
    """
    Eliminates variables that derive nothing.
    """
    prods = G.Productions

    accepted = {t.Name for t in G.terminals}   # Symbols that derives in some terminal string
    
    # Discovering all variables that derives in terminal strings
    change = True
    checked = set()
    while change:
        change = False
        for i in range(len(prods)):     # Iter over productions
            if i in checked:
                continue
            if all(s.Name in accepted for s in prods[i].Right):
                accepted.add(prods[i].Left.Name)
                checked.add(i)
                change = True
    
    # Removing all productions that have non accepted variables
    variables = [nt.Name for nt in G.nonTerminals]
    for i in range(len(prods)):
        if prods[i].Left.Name not in accepted \
        or any(s.Name in variables and s.Name not in accepted for s in prods[i].Right):
            prods[i] = None
    
    # Replacing old productions by new productions
    G.Productions = []          # Clean grammar productions
    for nt in G.nonTerminals:   # Clean non terminals productions
        nt.productions = []
    for p in prods:             # Add new productions
        if p is not None:
            G.Add_Production(p)
    # Removing non terminals with no productions
    for v in variables:
        if v not in accepted:
            G.nonTerminals.remove(G[v])
            G.symbDict.pop(v)
    # print(prods)


def remove_unreachable(G: Grammar):
    """
    Removes unreachable symbols from start symbol
    """
    prods = G.Productions
    reachables = {G.startSymbol.Name}
    
    # Finding unreachable symbols
    checked = set()
    change = True
    while change:
        change = False
        for i in range(len(prods)):
            if i in checked:
                continue
            if prods[i].Left.Name in reachables:
                right_set = {s.Name for s in prods[i].Right}
                if not right_set.issubset(reachables):
                    reachables = reachables.union(right_set)
                    change = True
                checked.add(i)

    # Removing all productions that have unreachable symbols
    for i in range(len(prods)):
        if prods[i].Left.Name not in reachables \
        or any(s.Name not in reachables for s in prods[i].Right):
            prods[i] = None
    
    # Replacing old productions by new productions
    G.Productions = []          # Clean grammar productions
    for nt in G.nonTerminals:   # Clean non terminals productions
        nt.productions = []
    for p in prods:             # Add new productions
        if p is not None:
            G.Add_Production(p)
    # Removing unreachable symbols
    symbols = [nt.Name for nt in G.nonTerminals]
    symbols.extend(t.Name for t in G.terminals)
    for s in symbols:
        if s not in reachables:
            try:
                G.nonTerminals.remove(G[s])
            except ValueError:
                G.terminals.remove(G[s])
            G.symbDict.pop(s)


def remove_left_recursion(G: Grammar):
    """
    Eliminates all left-recursion for any CFG with no e-productions and no cycles.
    """
    def has_lr(nt: NonTerminal) -> bool:
        """
        True if `nt` has left recursion.
        """
        return any(p.Left == p.Right[0] for p in nt.productions)
    
    prods = [p for p in G.Productions]
    new_prods = []
    for nt in G.nonTerminals:
        if has_lr(nt):
            new_symbol = G.NonTerminal(nt.Name + "'")
            for p in nt.productions:
                if p.Right[0] == p.Left:    # Production has the from A -> Axyz
                    new_right = [s for s in p.Right[1:]]
                    new_right.append(new_symbol)
                    new_prods.append(Production(new_symbol, Sentence(*new_right)))
                else:       # Production has the from A -> xyz
                    new_right = [s for s in p.Right[0:]]
                    new_right.append(new_symbol)
                    new_prods.append(Production(p.Left, Sentence(*new_right)))
            new_prods.append(Production(new_symbol, G.Epsilon))
        else:
            for p in nt.productions:
                new_prods.append(p)
    
    # Replacing old productions by new productions
    G.Productions = []          # Clean grammar productions
    for nt in G.nonTerminals:   # Clean non terminals productions
        nt.productions = []
    for p in new_prods:         # Add new productions
        G.Add_Production(p)

def remove_ambiguity(G: Grammar):
    """
    Transforms productions of a non terminal for remove ambiguity.
    """
    change = True
    while change:
        change = False
        prods = G.Productions

        for nt in G.nonTerminals:
            p_dict = {}     # pi.Right[0] : {p1, p2, ..., pn}
            for p in nt.productions:
                if p.IsEpsilon:
                    continue
                try:
                    p_dict[p.Right[0].Name].append(p)
                except KeyError:
                    p_dict[p.Right[0].Name] = [p]
            
            next_appendix = "'"
            for p_set in p_dict.values():
                if len(p_set) > 1:      # Means nt has ambiguous production (all in p_set)
                    new_left = G.NonTerminal(nt.Name + next_appendix)
                    next_appendix = next_appendix + "'"
                    for p in p_set:
                        new_right = p.Right[1:]
                        if len(new_right) == 0:
                            prods.append(Production(new_left, G.Epsilon))
                        else:
                            prods.append(Production(new_left, Sentence(*new_right)))
                        prods.remove(p)
                    prods.append(Production(nt, Sentence(p.Right[0], new_left)))
                    change = True

        # Replacing old productions by new productions
        G.Productions = []          # Clean grammar productions
        for nt in G.nonTerminals:   # Clean non terminals productions
            nt.productions = []
        for p in prods:             # Add new productions
            G.Add_Production(p)


class GrammarPipeline():
    def __init__(self, G: Grammar, methods: []):
        self.G = G
        self.methods = methods

    def run(self):
        for f in self.methods:
            f(self.G)

    def push(self, method):
        self.methods.append(method)

    def pop(self):
        self.methods.pop()
