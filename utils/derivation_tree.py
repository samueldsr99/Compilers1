import pydot


class Node:
    """
    Base Node class for derivation tree
    """
    def __init__(self, symbol, parent=None):
        self.children = []
        self.symbol = symbol
        self.parent = parent

    def append_child(self, symbol):
        """
        Adds a child node to self node
        """
        self.children.append(Node(symbol, parent=self))
        return self.children[-1]

    def root(self):
        """
        Returns reference to the root node
        """
        return self if self.parent is None else self.parent.root()

    def __str__(self):
        return str(self.symbol)


class DerivationTree:
    def __init__(self, productions):
        self.root = self._build_tree(productions)

    def _build_tree(self, productions):
        raise NotImplementedError

    def _derivation(self, productions, node=None):
        raise NotImplementedError

    def graph(self):
        G = pydot.Dot(graph_type='graph', rankdir='TD', margin=0.1)
        pending = [self.root]

        while pending:
            current = pending.pop()
            ids = id(current)
            G.add_node(pydot.Node(name=ids, label=str(current), shape='circle'))
            for child in current.children:
                pending.append(child)
                G.add_node(pydot.Node(name=id(child), label=str(child), shape='circle'))
                G.add_edge(pydot.Edge(ids, id(child)))

        return G

    def _repr_svg_(self):
        try:
            return self.graph().create_svg().decode('utf8')
        except AttributeError:
            pass

    def __str__(self):
        return str(self.root)


class LLDerivationTree(DerivationTree):
    def _build_tree(self, productions):
        iter_productions = iter(productions)
        return self._derivation(iter_productions)

    def _derivation(self, productions, node=None):
        try:
            head, body = next(productions)
        except StopIteration:
            return node.root()

        if node is None:
            node = Node(head)

        assert node.symbol == head

        for symbol in body:
            if symbol.IsTerminal:
                node.append_child(symbol)
            elif symbol.IsNonTerminal:
                next_node = node.append_child(symbol)
                self._derivation(productions, next_node)
        return node


class LRDerivationTree(DerivationTree):
    def _build_tree(self, productions):
        iter_productions = iter(reversed(productions))
        return self._derivation(iter_productions)

    def _derivation(self, productions, node=None):
        try:
            head, body = next(productions)
        except StopIteration:
            return node.root()

        if node is None:
            node = Node(head)

        assert node.symbol == head

        for symbol in reversed(body):
            if symbol.IsTerminal:
                node.append_child(symbol)
            elif symbol.IsNonTerminal:
                next_node = node.append_child(symbol)
                self._derivation(productions, next_node)
        node.children.reverse()
        return node
