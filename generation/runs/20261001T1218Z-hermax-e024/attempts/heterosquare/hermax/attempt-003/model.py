# Heterosquare: fill an n x n square with the distinct integers 1..n^2 so that
# the n row sums, the n column sums and the two diagonal sums are all different.
import functools
import itertools
import operator

from hermax.model import Model


def exactly_one(m, lits, name):
    """Post "exactly one of lits is true" with a ladder encoding.

    prefix[i] says that one of lits[0..i] is true; each literal sets its prefix,
    prefixes carry on, and a literal after a set prefix is forbidden. That takes
    three clauses per literal, where forbidding every pair takes a quadratic number.
    """
    prefix = m.bool_vector(name, len(lits))
    for i, lit in enumerate(lits):
        m &= (~lit | prefix[i])
        if i + 1 < len(lits):
            m &= (~prefix[i] | prefix[i + 1])
            m &= (~lits[i + 1] | ~prefix[i])
    m &= functools.reduce(operator.or_, lits)


def define(m, name, inputs, function):
    """Return a new Boolean that always equals function(*input values).

    The definition is posted as one clause per combination of input values: when
    the inputs take that combination, the new variable takes the function's value.
    """
    out = m.bool(name)
    for values in itertools.product((0, 1), repeat=len(inputs)):
        # "some input differs from this combination, or out has the function's value"
        clause = [~lit if v else lit for lit, v in zip(inputs, values)]
        clause.append(out if function(*values) else ~out)
        m &= functools.reduce(operator.or_, clause)
    return out


def add_numbers(m, numbers, width, name):
    """Add binary numbers (each a list of bits, least significant first).

    Returns the bits of the sum, least significant first, `width` of them: the
    caller passes the bit length of the largest possible sum, so no wider bits
    appear. The bits of each column are combined with full and half adders, whose
    carries go to the next column.
    """
    columns = [[] for _ in range(width)]
    for bits in numbers:
        for k, bit in enumerate(bits):
            columns[k].append(bit)
    result = []
    for k in range(width):
        column = columns[k]
        while len(column) >= 3:
            a, b, c = column.pop(0), column.pop(0), column.pop(0)
            column.append(define(m, f"{name}_s{k}_{len(column)}", [a, b, c], lambda x, y, z: x ^ y ^ z))
            if k + 1 < width:
                columns[k + 1].append(define(m, f"{name}_c{k}_{len(column)}", [a, b, c],
                                             lambda x, y, z: int(x + y + z >= 2)))
        if len(column) == 2:
            a, b = column
            column = [define(m, f"{name}_hs{k}", [a, b], lambda x, y: x ^ y)]
            if k + 1 < width:
                columns[k + 1].append(define(m, f"{name}_hc{k}", [a, b], lambda x, y: x & y))
        if column:
            result.append(column[0])
        else:  # no bit can reach this column: it is 0
            zero = m.bool(f"{name}_zero{k}")
            m &= ~zero
            result.append(zero)
    return result


def build(instance):
    n = instance["n"]  # order of the square
    cells = n * n  # the entries are 1..cells
    value_bits = cells.bit_length()  # binary digits needed for an entry

    m = Model()
    # x[i][j] = the entry in row i, column j (the declared output)
    x = m.int_matrix("x", n, n, 1, cells)
    # holds[(i, j)][v - 1] = the cell (i, j) contains v (one-hot form of x)
    holds = {(i, j): m.bool_vector(f"holds_{i}_{j}", cells) for i in range(n) for j in range(n)}

    # every cell holds one value and every value is in one cell, so all entries are different
    for (i, j), row in holds.items():
        exactly_one(m, [row[v] for v in range(cells)], f"cell_{i}_{j}")
    for v in range(cells):
        exactly_one(m, [holds[(i, j)][v] for (i, j) in holds], f"value_{v + 1}")
    # x shows the value held: holding v means x >= v and not x >= v + 1
    for (i, j), row in holds.items():
        for v in range(1, cells + 1):
            if v > 1:
                m &= (~row[v - 1] | (x[i][j] >= v))
            if v < cells:
                m &= (~row[v - 1] | ~(x[i][j] >= v + 1))

    # Binary digits of every entry, so that the line sums can be added with
    # adders: digit k of the cell is on exactly when the value it holds has it on.
    bits = {}
    for (i, j), row in holds.items():
        bits[(i, j)] = m.bool_vector(f"bits_{i}_{j}", value_bits)
        for v in range(1, cells + 1):
            for k in range(value_bits):
                m &= (~row[v - 1] | (bits[(i, j)][k] if (v >> k) & 1 else ~bits[(i, j)][k]))

    # The n row sums, n column sums and two diagonal sums. A line adds n entries
    # of at most `cells`, so a sum has at most this many binary digits.
    width = (n * cells).bit_length()
    lines = ([[(i, j) for j in range(n)] for i in range(n)]  # row i
             + [[(j, i) for j in range(n)] for i in range(n)]  # column i
             + [[(i, i) for i in range(n)], [(i, n - 1 - i) for i in range(n)]])  # the two diagonals
    sums = [add_numbers(m, [list(bits[cell]) for cell in line], width, f"line_{index}")
            for index, line in enumerate(lines)]

    # All line sums are different: for every two lines, some binary digit of their
    # sums differs. differs[k] is only allowed to be true where the digits do differ.
    for a in range(len(sums)):
        for b in range(a + 1, len(sums)):
            differs = m.bool_vector(f"differs_{a}_{b}", width)
            for k in range(width):
                m &= (~differs[k] | sums[a][k] | sums[b][k])
                m &= (~differs[k] | ~sums[a][k] | ~sums[b][k])
            m &= differs.at_least_one()

    return m, {"x": x}
