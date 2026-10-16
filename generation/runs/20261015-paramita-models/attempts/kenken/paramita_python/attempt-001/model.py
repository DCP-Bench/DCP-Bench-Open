# KenKen: fill the n x n grid with digits 1 to n so that each row and each column
# holds every digit exactly once, and each cage's digits achieve its target under
# one of the arithmetic operations. The operation of each cage is not given.
from itertools import product as cartesian

from paramita.modelling import Bool, If, Or


def build(instance):
    n = instance["n"]
    digits = range(1, n + 1)
    cells_all = [(r, c) for r in range(1, n + 1) for c in range(1, n + 1)]

    # one-hot encoding: xv[(r, c)][v] is true when cell (r, c) holds digit v
    xv = {cell: {v: Bool(f"x_{cell[0]}_{cell[1]}_{v}") for v in digits} for cell in cells_all}

    cons = []

    # each cell holds exactly one digit
    for cell in cells_all:
        cons.append(sum(xv[cell].values()) == 1)

    # each row contains exactly one of each digit
    for r in range(1, n + 1):
        for v in digits:
            cons.append(sum(xv[(r, c)][v] for c in range(1, n + 1)) == 1)

    # each column contains exactly one of each digit
    for c in range(1, n + 1):
        for v in digits:
            cons.append(sum(xv[(r, c)][v] for r in range(1, n + 1)) == 1)

    # each cage: its digits achieve the target under one of the operations
    for ci, (target, cage_cells) in enumerate(instance["problem"]):
        cells = [tuple(cell) for cell in cage_cells]
        tag = f"cage_{ci}"

        # a single-cell cage: the cell holds the target
        if len(cells) == 1:
            cons.append(xv[cells[0]][target])
            continue

        flags = []

        # sum: the digits of the cage add up to the target
        sum_flag = Bool(f"{tag}_sum")
        flags.append(sum_flag)
        cons.append(If(
            sum_flag,
            sum(v * xv[cell][v] for cell in cells for v in digits) == target,
        ))

        # the table of digit tuples that satisfy an operation is encoded
        # with one Bool per tuple; the tuple Bools only fix the cells they name
        def table_op(name, allowed):
            flag = Bool(f"{tag}_{name}")
            flags.append(flag)
            if not allowed:
                cons.append(~flag)
                return
            tuple_bools = []
            for i, tup in enumerate(allowed):
                p = Bool(f"{tag}_{name}_{i}")
                for cell, v in zip(cells, tup):
                    cons.append(If(p, xv[cell][v]))
                tuple_bools.append(p)
            cons.append(If(flag, Or(tuple_bools)))

        # product: the digits of the cage multiply to the target
        product_tuples = [t for t in cartesian(digits, repeat=len(cells))
                          if _product(t) == target]
        table_op("product", product_tuples)

        # a two-cell cage may also use difference or exact quotient
        if len(cells) == 2:
            diff_tuples = [t for t in cartesian(digits, repeat=2)
                           if abs(t[0] - t[1]) == target]
            table_op("difference", diff_tuples)

            quot_tuples = [t for t in cartesian(digits, repeat=2)
                           if max(t) == target * min(t)]
            table_op("quotient", quot_tuples)

        # the cage satisfies at least one of its operations
        cons.append(Or(flags))

    # solved grid: the digit in each cell
    x = []
    for r in range(1, n + 1):
        x.append([sum(v * xv[(r, c)][v] for v in digits) for c in range(1, n + 1)])

    return cons, {"x": x}


def _product(tup):
    result = 1
    for v in tup:
        result *= v
    return result
