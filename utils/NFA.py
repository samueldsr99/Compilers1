try:
    import pydot
except:
    pass

from cmp.utils import ContainerSet

class NFA:
    def __init__(self, states, finals, transitions, start=0):
        self.states = states
        self.start = start
        self.finals = set(finals)
        self.map = transitions
        self.vocabulary = set()
        self.transitions = { state: {} for state in range(states) }
        
        for (origin, symbol), destinations in transitions.items():
            assert hasattr(destinations, '__iter__'), 'Invalid collection of states'
            self.transitions[origin][symbol] = destinations
            self.vocabulary.add(symbol)
            
        self.vocabulary.discard('')

    def epsilon_transitions(self, state):
        assert state in self.transitions, 'Invalid state'
        try:
            return self.transitions[state]['']
        except KeyError:
            return ()

    def graph(self):
        G = pydot.Dot(rankdir='LR', margin=0.1)
        G.add_node(pydot.Node('start', shape='plaintext', label='', width=0, height=0))

        for (start, tran), destinations in self.map.items():
            tran = 'ε' if tran == '' else tran
            G.add_node(pydot.Node(start, shape='circle', style='bold' if start in self.finals else ''))
            for end in destinations:
                G.add_node(pydot.Node(end, shape='circle', style='bold' if end in self.finals else ''))
                G.add_edge(pydot.Edge(start, end, label=tran, labeldistance=2))

        G.add_edge(pydot.Edge('start', self.start, label='', style='dashed'))
        return G

    def _repr_svg_(self):
        try:
            return self.graph().create_svg().decode('utf8')
        except:
            pass

    def move(self, states, symbol):
        moves = set()
        for state in states:
            # Your code here
            try:
                moves.update(set(self.transitions[state][symbol]))
            except KeyError:
                pass
        return moves

    def epsilon_closure(self, states):
        pending = [ s for s in states ] # equivalente a list(states) pero me gusta así :p
        closure = { s for s in states } # equivalente a  set(states) pero me gusta así :p
        
        while pending:
            state = pending.pop()
            # Your code here
            for x in self.epsilon_transitions(state):
                if x not in closure:
                    closure.add(x)
                    pending.append(x)
        return ContainerSet(*closure)

    def to_dfa(self):
        from .DFA import DFA

        transitions = {}
        
        start = self.epsilon_closure([self.start])
        start.id = 0
        start.is_final = any(s in self.finals for s in start)
        states = [ start ]

        pending = [ start ]
        while pending:
            state = pending.pop()
            
            for symbol in self.vocabulary:
                # Your code here
                # ...
                moves = self.move(state, symbol)
                e_closure = self.epsilon_closure(moves)
                if not e_closure:
                    continue
                if e_closure not in states:
                    e_closure.id = len(states)
                    e_closure.is_final = any(s in self.finals for s in e_closure)
                    states.append(e_closure)
                    pending.append(e_closure)
                else:
                    e_closure = states[states.index(e_closure)]
                try:
                    transitions[state.id, symbol]
                    assert False, 'Invalid DFA!!!'
                except KeyError:
                    # Your code here
                    transitions[state.id, symbol] = e_closure.id
                    pass
        finals = [ state.id for state in states if state.is_final ]
        dfa = DFA(len(states), finals, transitions)
        return dfa

    @staticmethod
    def extend_automaton(automaton):
        """
        returns new NFA-automaton with a single final state distinct from start state
        can be called from DFA
        """

        start = automaton.states
        states = start + 1

        # Add epsilon transition from new start to previous start
        
        transitions = {(start, ''): [automaton.start]}

        for st, d2 in automaton.transitions.items():
            for symbol, nst in d2.items():
                transitions[(st, symbol)] = nst

        # add new final state
        final = states
        states += 1

        for f in automaton.finals:
            transitions[(f, '')] = [final]

        return NFA(states, [final], transitions, start)

    
    def _build_adj_list(self, adj_list, r_adj_list):
        for i in range(self.states):
            adj_list[i] = {}
            r_adj_list[i] = {}
        
        for a, d2 in self.transitions.items():
            for symbol, t in d2.items():
                for b in t:
                    if not adj_list.get(a):
                        adj_list[a] = {}
                    if not r_adj_list.get(b):
                        r_adj_list[b] = {}

                    if adj_list[a].get(b) == None:
                        adj_list[a][b] = symbol
                    else:
                        adj_list[a][b] = append_or(adj_list[a][b], symbol)
                    if r_adj_list[b].get(a) == None:
                        r_adj_list[b][a] = symbol
                    else:
                        r_adj_list[b][a] = append_or(r_adj_list[b][a], symbol)

    def to_regex(self):
        removed = set()
        adj_list = {}
        r_adj_list = {}
        self._build_adj_list(adj_list, r_adj_list)

        assert len(self.finals) == 1, 'Automaton must be aumgented'

        final = list(self.finals)[0]

        recognize_epsilon = final in self.epsilon_closure([self.start])

        states_to_remove = [state for state in range(self.states) if state not in [self.start, final]]

        from random import shuffle
        shuffle(states_to_remove)

        for x in states_to_remove:
            if not adj_list.get(x):
                # does not have next state
                remove_state(x, adj_list, r_adj_list)
                removed.add(x)
                continue
            try:
                if len(adj_list[x][x]) == 1:
                    sx = '{}*'.format(adj_list[x][x])
                else:
                    sx = '({})*'.format(adj_list[x][x])
            except KeyError:
                sx = ''
            for b, sb in adj_list[x].items():
                if b in removed:
                    continue
                for a, sa in r_adj_list[x].items():
                    if a in removed:
                        continue

                    new_regex = ''
                    if sa:
                        if len(sa) == 1 or ( sa[0] == '(' and sa[-1] == ')' ):
                            new_regex += sa
                        else:
                            new_regex += "({})".format(sa)
                    new_regex += sx
                    if sb:
                        if sx and sx[-1] == '*' and sx[1:-2] == sb:
                            pass
                        elif len(sb) == 1 or ( sb[0] == '(' and sb[-1] == ')' ):
                            new_regex += sb
                        else:
                            new_regex += "({})".format(sb)
                    
                    if adj_list[a].get(b) == None:
                        adj_list[a][b] = new_regex
                    else:
                        adj_list[a][b] = append_or(adj_list[a][b], new_regex)

                    if r_adj_list[b].get(a) == None:
                        r_adj_list[b][a] = new_regex
                    else:
                        r_adj_list[b][a] = append_or(r_adj_list[b][a], new_regex)
            
            remove_state(x, adj_list, r_adj_list)
        
        regex = adj_list[self.start][final]
        if recognize_epsilon:
            return append_or('', regex)
        return regex

    def get_regex(self, it=20):
        shorter = self.to_regex()
        for _ in range(it):
            aux = self.to_regex()
            if len(shorter) > len(aux):
                shorter = aux

        return shorter

#################################################### Utils ####################################################

def append_or(s, new_s):
    # append or verifying that does not exists in s n
    append = True
    for sub in s.split('|'):
        if sub == new_s:
            append = False
    if append:
        return '{}|{}'.format(s, new_s)
    return s

def remove_state(state, adj_list, r_adj_list):
    adj_list[state] = {}
    r_adj_list[state] = {}
    
    for i in adj_list.keys():
        try:
            adj_list[i].pop(state)
        except KeyError:
            pass
    
    for i in r_adj_list.keys():
        try:
            r_adj_list[i].pop(state)
        except KeyError:
            pass
