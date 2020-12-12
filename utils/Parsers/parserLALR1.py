from utils.Parsers.parserLR1 import *

def build_LALR1_automaton(G, firsts=None):
    assert len(G.startSymbol.productions) == 1, 'Grammar must be augmented'

    if not firsts:
        firsts = compute_firsts(G)
    firsts[G.EOF] = ContainerSet(G.EOF)

    start_production = G.startSymbol.productions[0]
    start_item = Item(start_production, 0, lookaheads=ContainerSet(G.EOF))
    start = frozenset([start_item.Center()])

    closure = closure_lr1([start_item], firsts)
    automaton = State(frozenset(closure), True)

    pending = [start]
    visited = {start: automaton}

    while pending:
        current = pending.pop()
        current_state = visited[current]

        current_closure = current_state.state
        for symbol in G.terminals + G.nonTerminals:
            goto = goto_lr1(current_closure, symbol, just_kernel=True)
            closure = closure_lr1(goto, firsts)
            center = frozenset(item.Center() for item in goto)

            if center == frozenset():
                continue

            try:
                next_state = visited[center]
                centers = {item.Center(): item for item in next_state.state}
                centers = {
                    item.Center(): (centers[item.Center()], item)
                    for item in closure
                }

                updated_items = set()
                for c, (itemA, itemB) in centers.items():
                    item = Item(c.production, c.pos,
                                itemA.lookaheads | itemB.lookaheads)
                    updated_items.add(item)

                updated_items = frozenset(updated_items)
                if next_state.state != updated_items:
                    pending.append(center)
                next_state.state = updated_items
            except KeyError:
                visited[center] = next_state = State(frozenset(closure), True)
                pending.append(center)

            if current_state[symbol.Name] is None:
                current_state.add_transition(symbol.Name, next_state)
            else:
                assert current_state.get(
                    symbol.Name) is next_state, 'Bad build!!!'

    automaton.set_formatter(multiline_formatter)
    return automaton


class LALR1Parser(LR1Parser):
    def _build_automaton(self):
        return build_LALR1_automaton(self.augmented_G, firsts=self.firsts)
