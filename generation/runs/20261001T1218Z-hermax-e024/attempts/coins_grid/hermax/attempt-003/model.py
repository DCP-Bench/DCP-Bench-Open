# Coins grid: place coins on an n by n grid, at most one per cell, with exactly
# c coins in every row and every column, so that the sum of the squared
# horizontal distances of the coins from the main diagonal is as small as possible.
import functools
import itertools
import operator

from hermax.model import Model


def define(m, inputs, function):
    """A new literal that equals function(*inputs) for 0/1 inputs, as clauses."""
    out = m.bool()
    for values in itertools.product((0, 1), repeat=len(inputs)):
        clause = [~lit if value else lit for lit, value in zip(inputs, values)]
        clause.append(out if function(*values) else ~out)
        m &= functools.reduce(operator.or_, clause)
    return out


def add_bits(m, xs, ys):
    """Binary sum of two numbers given as lists of literals, least significant
    bit first. An entry None stands for a bit that is always 0."""
    result = []
    carry = None
    for i in range(max(len(xs), len(ys))):
        terms = [t for t in (xs[i] if i < len(xs) else None,
                             ys[i] if i < len(ys) else None, carry) if t is not None]
        if len(terms) == 0:
            result.append(None)
            carry = None
        elif len(terms) == 1:
            result.append(terms[0])
            carry = None
        elif len(terms) == 2:
            result.append(define(m, terms, lambda a, b: a ^ b))
            carry = define(m, terms, lambda a, b: a & b)
        else:
            result.append(define(m, terms, lambda a, b, c: a ^ b ^ c))
            carry = define(m, terms, lambda a, b, c: (a & b) | (a & c) | (b & c))
    if carry is not None:
        result.append(carry)
    return result


def literal_and(m, x, y):
    """x AND y for literals or the constants True / False."""
    if x is False or y is False:
        return False
    if x is True:
        return y
    if y is True:
        return x
    return define(m, [x, y], lambda a, b: a & b)


def literal_or(m, x, y):
    """x OR y for literals or the constants True / False."""
    if x is True or y is True:
        return True
    if x is False:
        return y
    if y is False:
        return x
    return define(m, [x, y], lambda a, b: a | b)


def integer_from_bits(m, bits, name):
    """An integer variable equal to the binary number with the given bits
    (least significant first; None is a bit that is always 0).

    Its order-encoding literal (z >= t) is tied to a comparison of the bits with
    t. The comparison is built from the top bit down and shared between values
    of t, so the whole link has about 2**len(bits) gates. Adding the bits as
    scaled integers instead makes every partial sum a wide integer, which is far
    larger.
    """
    width = len(bits)
    z = m.int(name, 0, 2 ** width - 1)
    memo = {}

    def at_least(level, t):
        """The number formed by the lowest `level` bits is at least t."""
        if t <= 0:
            return True
        if t >= 2 ** level:
            return False
        if (level, t) not in memo:
            top = bits[level - 1] if bits[level - 1] is not None else False
            half = 2 ** (level - 1)
            if t >= half:  # needs the top bit and enough in the rest
                memo[(level, t)] = literal_and(m, top, at_least(level - 1, t - half))
            else:  # the top bit alone is enough, or the rest is
                memo[(level, t)] = literal_or(m, top, at_least(level - 1, t))
        return memo[(level, t)]

    for t in range(1, 2 ** width):
        holds = at_least(width, t)
        if holds is True:
            m &= (z >= t)
        elif holds is False:
            m &= ~(z >= t)
        else:
            m &= (~(z >= t) | holds)
            m &= ((z >= t) | ~holds)
    return z


def build(instance):
    n = instance["n"]  # side of the grid
    c = instance["c"]  # coins in each row and each column

    m = Model()
    # x[i][j] = 1 if there is a coin in cell (i, j), otherwise 0 (at most one per cell)
    x = m.int_matrix("x", n, n, 0, 1)
    # coin[i][j] is the literal "there is a coin in cell (i, j)"
    coin = [[x[i][j] >= 1 for j in range(n)] for i in range(n)]

    for i in range(n):
        # every row holds exactly c coins
        m &= (sum(x[i][j] for j in range(n)) == c)
        # every column holds exactly c coins
        m &= (sum(x[j][i] for j in range(n)) == c)

    # A coin in cell (i, j) is (i - j)^2 away from the diagonal. Minimise the sum:
    # each coin pays its distance (a soft clause pays when its literal is false,
    # so the literal is the negation of "there is a coin").
    for i in range(n):
        for j in range(n):
            if i != j:
                m.obj[(i - j) ** 2] += ~coin[i][j]

    # z, the sum of those distances, is a declared output. Equating a variable to
    # a sum with 100 or more weighted terms through hermax's integer encoding ran
    # out of memory on the larger grids, so the sum is built as a binary number
    # with adder circuits over the coin literals (each coin adds its distance,
    # written in binary) and the bits are then tied to an integer variable.
    total = None
    for i in range(n):
        for j in range(n):
            distance = (i - j) ** 2
            if distance == 0:
                continue
            term = [coin[i][j] if (distance >> k) & 1 else None
                    for k in range(distance.bit_length())]
            total = term if total is None else add_bits(m, total, term)
    if total is None:  # a 1 x 1 grid has no distance to add
        total = [None]
    z = integer_from_bits(m, total, "z")

    return m, {"x": x, "z": z}
