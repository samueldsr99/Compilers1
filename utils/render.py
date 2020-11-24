import pandas as pd

from utils.first_follow import compute_firsts, compute_follows
from utils.parser import build_parsing_table


def LL1_to_dataframe(G):
    firsts = compute_firsts(G)
    follows = compute_follows(G, firsts)
    M = build_parsing_table(G, firsts, follows)

    rows, columns = set(), set()
    matrix = []

    for item in M:
        rows.add(item[0])
        columns.add(item[1])

    for row in rows:
        matrix.append([])
        for column in columns:
            try:
                production = M[row, column][0]
                matrix[-1].append(
                    str(production.Left) + ' -> ' +
                    str(production.Right)
                )
            except KeyError:
                matrix[-1].append(' ')

    return pd.DataFrame(matrix, index=rows, columns=columns)


def LR_table_to_dataframe(d: dict):
    rows, columns = set(), set()
    matrix = []

    for item in d:
        rows.add(item[0])
        columns.add(item[1])

    for row in rows:
        matrix.append([])
        for column in columns:
            try:
                cell = d[row, column]
                matrix[-1].append(cell)
            except KeyError:
                matrix[-1].append(' ')

    return pd.DataFrame(matrix, index=rows, columns=columns)
