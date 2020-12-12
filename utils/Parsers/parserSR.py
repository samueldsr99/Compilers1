SHIFT_REDUCE = 0
REDUCE_REDUCE = 1


class Conflict:
    def __init__(self, type, key, value):
        self.type = type
        self.key = key
        self.value = value


class ShiftReduceParser:
    SHIFT = 'SHIFT'
    REDUCE = 'REDUCE'
    OK = 'OK'

    def __init__(self, G, verbose=False):
        self.G = G
        self.verbose = verbose
        self.action = {}
        self.goto = {}
        self.conflicts = []
        self._build_parsing_table()

    def _register(self, table, key, value):
        if key in table and value not in table[key]:
            if table[key][0][0] == self.REDUCE and value[0] == self.REDUCE:
                type = REDUCE_REDUCE
            else:
                type = SHIFT_REDUCE
            self.conflicts.append(Conflict(type, (key[0], key[1]), (table[key][0], value)))
            table[key].append(value)
        table[key] = [value]

    def _build_parsing_table(self):
        raise NotImplementedError()

    def __call__(self, w):
        stack = [0]
        cursor = 0
        output = []

        while True:
            state = stack[-1]
            lookahead = w[cursor]
            if self.verbose:
                print(stack, '<---||--->', w[cursor:])

            # Your code here!!! (Detect error)
            if (state, lookahead) not in list(self.action.keys()):
                print(f'Error in state {state}, lookahead {lookahead}.')
                return None

            action, tag = self.action[state, lookahead][0]
            # Your code here!!! (Shift case)
            if action == self.SHIFT:
                cursor += 1
                stack += [lookahead, tag]
            # Your code here!!! (Reduce case)
            elif action == self.REDUCE:
                output.append(tag)
                left, right = tag
                for symbol in reversed(right):
                    stack.pop()
                    assert stack.pop() == symbol, f'Parsing Error in Reduce case: {tag}'
                state = stack[-1]
                goto = self.goto[state, left][0]
                stack += [left, goto]
            # Your code here!!! (OK case)
            elif action == self.OK:
                stack.pop()
                assert stack.pop() == self.G.startSymbol, 'Parsing error in OK case'
                assert len(stack) == 1, 'Error: parsing ended with symbols in stack.'
                return output
            # Your code here!!! (Invalid case)
            else:
                raise Exception('Error: Wrong action.')
