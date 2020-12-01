from cmp.pycompiler import Item
from cmp.utils import ContainerSet
from utils.first_follow import compute_firsts
from cmp.automata import State
from utils.Parsers.parserSR import ShiftReduceParser
from .parserLR1 import closure_lr1, compress, goto_lr1
from .parserSLR1 import build_LR0_automaton


def build_lalr_automaton(G):

    def centers(items: [Item]):
        return frozenset(item.Center() for item in items)

    def lookaheads(items: [Item]):
        return {item.Center(): item.lookaheads for item in items}

    def subset(items1, items2):
        return all(items1[i] <= items2[i] for i in items1)


    assert len(G.startSymbol.productions) == 1, 'Grammar must be augmented'
    firsts = compute_firsts(G)
    firsts[G.EOF] = ContainerSet(G.EOF)

    start_production = G.startSymbol.productions[0]
    start_item = Item(start_production, 0, (G.EOF,))

    start = State(frozenset(closure_lr1([start_item], firsts)), True)

    pending = [start_item]
    visisted_centers = {centers(start.state): start}
    visited = {start_item: start}

    while pending:
        current_state = visited[pending.pop()]
        for symbol in G.terminals + G.nonTerminals:
            next_item = frozenset(goto_lr1(current_state.state, symbol, firsts))

            if next_item:
                try:
                    next_state = visisted_centers[centers(next_item)]
                    if not subset(lookaheads(next_item), lookaheads(next_state.state)):
                        next_state.state = compress(list(next_state.state) + list(next_item))
                        pending.append(frozenset(next_state.state))
                        visited[frozenset(next_state.state)] = next_state
                except KeyError:
                    next_state = State(next_item,True)
                    pending += [next_item]
                    visisted_centers[centers(next_item)] = next_state
                    visited[next_item] = next_state
                current_state.add_transition(symbol.Name, next_state)

    return start


# def get_lookaheads(st, prop, table, firsts):
#     for kernel in st.state:
#         closure = closure_lr1([Item(kernel.production, kernel.pos, ('#',))], firsts)
#         for item in closure:
#             if item.IsReduceItem:
#                 continue

#             next_state = st.get(item.NextSymbol.name)
#             next_item = item.NextItem().Center()
#             if '#' in item.lookaheads:
#                 prop[st, kernel].append((next_state, next_item))
#             table[next_state, next_item].extend(item.lookaheads - {'#'})


# def build_lalr_automaton(G):
#     automaton = build_LR0_automaton(G)

#     firsts = compute_firsts(G)
#     firsts[G.EOF] = ContainerSet(G.EOF)

#     print(type(automaton))
#     for st in automaton:
#         print(st, st.state, type(st.state))
#     table = {(st, item): ContainerSet() for st in automaton for item in st.state}
#     cl = {(st, item): [] for st in automaton for item in st.state}

#     for st in automaton:
#         get_lookaheads(st, cl, table, firsts)
#     del firsts['#']

#     start_item = list(automaton.state).pop()
#     table[automaton, start_item] = ContainerSet(G.EOF)

#     pending = True
#     while pending:
#         pending = False
#         for from_state, from_item in cl:
#             for to_state, to_item in cl[from_state, from_item]:
#                 change |= table[to_state, to_item].extend(table[from_state, from_item])

#     for st in automaton:
#         st.state = frozenset(closure_lr1(st.state, firsts))

#     return automaton


class LALRParser(ShiftReduceParser):
    def _build_parsing_table(self):
        G = self.G.AugmentedGrammar()
        automaton = build_lalr_automaton(G)
        for i, node in enumerate(automaton):
            node.idx = i

        for node in automaton:
            idx = node.idx
            for item in node.state:
                if item.IsReduceItem:
                    if item.production.Left == G.startSymbol:
                        self.register(self.action, (idx, G.EOF), ('OK', item.production))
                    else:
                        for lookahead in item.lookaheads:
                            self.register(self.action, (idx, lookahead), ('REDUCE', item.production))
                else:
                    next_symbol = item.NextSymbol
                    try:
                        if next_symbol.IsNonTerminal:
                            next_state = node.transitions[next_symbol.Name][0]
                            self.register(self.goto, (idx, next_symbol), next_state.idx)
                        else:
                            next_state = node.transitions[next_symbol.Name][0]
                            self.register(self.action, (idx, next_symbol), ('SHIFT', next_state.idx))
                    except KeyError:
                        pass

    @staticmethod
    def _register(table, key, value):
        if key in table and table[key] != value:
            raise Exception('Shift-Reduce or Reduce-Reduce conflict!!!')
        table[key] = value
