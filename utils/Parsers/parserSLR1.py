from cmp.automata import State
from cmp.pycompiler import Item
from utils.Parsers.parserSR import ShiftReduceParser
from utils.first_follow import compute_firsts, compute_follows


def build_LR0_automaton(G):
    assert len(G.startSymbol.productions) == 1, 'Grammar must be augmented'

    start_production = G.startSymbol.productions[0]
    start_item = Item(start_production, 0)

    automaton = State(start_item, True)

    pending = [start_item]
    visited = {start_item: automaton}

    while pending:
        current_item = pending.pop()
        if current_item.IsReduceItem:
            continue

        # Your code here!!! (Decide which transitions to add)
        current_state = visited[current_item]
        next_symbol = current_item.NextSymbol
        next_item = current_item.NextItem()
        try:
            next_state = visited[next_item]
        except KeyError:
            next_state = State(next_item, True)
            visited[next_item] = next_state
        current_state.add_transition(next_symbol.Name, next_state)
        # print('Added trans:  ', current_state, f'==={next_symbol.Name}===>', next_state)
        pending.append(next_item)

        if next_symbol.IsNonTerminal:   # If symbol is non terminal, add e-productions to Y->.alpha
            for prod in next_symbol.productions:
                new_item = Item(prod, 0)
                try:
                    new_state = visited[new_item]
                    item_was_found = True
                except KeyError:
                    new_state = State(new_item, True)
                    visited[new_item] = new_state
                    item_was_found = False
                current_state.add_epsilon_transition(new_state)
                # print('Added e-trans:', current_state, '==>', new_state)
                if not item_was_found:
                    pending.append(new_item)

    return automaton


class SLR1Parser(ShiftReduceParser):

    def _build_parsing_table(self):
        G = self.G.AugmentedGrammar(True)
        firsts = compute_firsts(G)
        follows = compute_follows(G, firsts)

        automaton = build_LR0_automaton(G).to_deterministic()
        for i, node in enumerate(automaton):
            if self.verbose:
                print(i, '\t', '\n\t '.join(str(x) for x in node.state), '\n')
            node.idx = i

        for node in automaton:
            idx = node.idx
            for state in node.state:
                item = state.state
                # Your code here!!!
                # - Fill `self.Action` and `self.Goto` according to `item`)
                # - Feel free to use `self._register(...)`)
                if item.IsReduceItem:
                    prod = item.production
                    if prod.Left == G.startSymbol:
                        self._register(self.action, (idx, G.EOF), (self.OK, None))
                    else:
                        for t in follows[prod.Left]:
                            self._register(self.action, (idx, t), (self.REDUCE, prod))
                else:
                    symbol = item.NextSymbol
                    goto_id = node.get(symbol.Name).idx
                    if goto_id is not None:
                        if symbol.IsTerminal:
                            self._register(self.action, (idx, symbol), (self.SHIFT, goto_id))
                        else:
                            self._register(self.goto, (idx, symbol), goto_id)
