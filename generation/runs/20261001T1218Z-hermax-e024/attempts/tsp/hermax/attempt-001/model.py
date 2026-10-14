# Travelling salesman: given the locations of cities, find the shortest round trip that
# visits every city exactly once and returns to the start. The distance between two
# cities is their Euclidean distance rounded to an integer, and the answer is the length
# of the shortest trip.
import math


def ranged_int(m, name, lo, hi):
    """An integer variable with values lo..hi. hermax wants at least two values, so a
    single-value range gets one spare value that is ruled out."""
    if lo < hi:
        return m.int(name, lo, hi)
    x = m.int(name, lo, lo + 1)
    m &= ~(x >= lo + 1)
    return x
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


def sum_bits(m, terms):
    """Bits (least significant first) of the sum of weight * [literal] over
    (weight, literal) pairs. The running sum is cut to the bit length of the
    largest value it can reach, since the bits above that are always false."""
    total, high = [None], 0
    for weight, lit in terms:
        term = [lit if (weight >> k) & 1 else None for k in range(weight.bit_length())]
        total = add_bits(m, total, term)
        high += weight
        total = total[:max(1, high.bit_length())]
    return total


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
    of t, so the whole link has about 2**len(bits) gates.
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
    locations = instance["locations"]  # locations[i] = [x, y] of city i
    n = len(locations)
    # distance[i][j] = Euclidean distance between cities i and j, rounded (the same
    # definition as the reference)
    distance = [[int(round(math.hypot(locations[i][0] - locations[j][0],
                                      locations[i][1] - locations[j][1])))
                 for j in range(n)] for i in range(n)]

    m = Model()
    # go[i][j] = the trip goes from city i directly to city j
    go = m.bool_matrix("go", n, n)

    # Every city is left once and entered once, and no city goes to itself: the trip
    # is a set of cycles that covers the cities.
    for i in range(n):
        m &= ~go[i][i]
        m &= go.row(i).exactly_one()
        m &= go.col(i).exactly_one()

    # Implied for n > 2: the trip never goes from i to j and straight back.
    if n > 2:
        for i in range(n):
            for j in range(i + 1, n):
                m &= (~go[i][j] | ~go[j][i])

    # The cycles form a single trip. City 0 is where the trip starts; position[i] is
    # the place of city i in the trip (1 to n - 1 for the other cities). Every step
    # between two cities other than city 0 moves forward by at least one place, which
    # no cycle that avoids city 0 could do, so the only cycle is the one through city 0.
    # (This is an order-encoding form of the Miller-Tucker-Zemlin constraints.)
    position = {i: ranged_int(m, f"position_{i}", 1, n - 1) for i in range(1, n)}
    for i in range(1, n):
        for j in range(1, n):
            if i != j:
                # if the trip goes from i to j then position[i] + 1 <= position[j]
                for t in range(1, n):
                    lits = [~go[i][j]]
                    if t > 1:
                        lits.append(~(position[i] >= t))
                    if t + 1 <= n - 1:
                        lits.append(position[j] >= t + 1)
                    clause = lits[0]
                    for lit in lits[1:]:
                        clause = clause | lit
                    m &= clause

    # Symmetry breaking (does not change the declared output, the trip length): when
    # distances are symmetric, a trip driven backwards has the same length, and it puts
    # city 1 after city 2 if it was before. Requiring city 1 to come before city 2
    # keeps one of the two directions.
    symmetric = all(distance[i][j] == distance[j][i] for i in range(n) for j in range(n))
    if symmetric and n > 3:
        for t in range(1, n):
            lits = []
            if t > 1:
                lits.append(~(position[1] >= t))
            if t + 1 <= n - 1:
                lits.append(position[2] >= t + 1)
            if lits:
                clause = lits[0]
                for lit in lits[1:]:
                    clause = clause | lit
                m &= clause

    # Minimise the length of the trip. A soft clause pays when its literal is false, so
    # each leg that is driven pays its distance through the negation of the literal.
    for i in range(n):
        for j in range(n):
            if i != j and distance[i][j] > 0:
                m.obj[distance[i][j]] += ~go[i][j]

    # travel_distance is a declared output. Tying an integer variable to a sum of
    # hundreds of weighted terms through hermax's integer encoding is slow, so it is
    # built as a binary number. Each city is left by exactly one leg, so bit b of the
    # distance of the leg leaving city i is on if the chosen leg has bit b on (an "or"
    # over the legs that have it); these n numbers are added with adder circuits.
    total, high = [None], 0
    for i in range(n):
        leg = []
        for b in range(max(distance[i]).bit_length()):
            having = [go[i][j] for j in range(n) if j != i and (distance[i][j] >> b) & 1]
            if not having:
                leg.append(None)
                continue
            bit = m.bool()
            m &= (~bit | functools.reduce(operator.or_, having))
            for lit in having:
                m &= (~lit | bit)
            leg.append(bit)
        total = add_bits(m, total, leg)
        high += max(distance[i])
        total = total[:max(1, high.bit_length())]  # the bits above the largest sum are 0
    travel_distance = integer_from_bits(m, total, "travel_distance")

    return m, {"travel_distance": travel_distance}
