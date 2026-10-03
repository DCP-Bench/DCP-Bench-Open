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


def exactly_one(m, lits, name):
    """Post "exactly one of lits is true" with a ladder encoding and return the prefix
    literals: prefix[i] says that one of lits[0..i] is true; each literal sets its
    prefix, prefixes carry on, and a literal after a set prefix is forbidden. That takes
    three clauses per literal, where forbidding every pair takes a quadratic number."""
    prefix = m.bool_vector(name, len(lits))
    for i, lit in enumerate(lits):
        m &= (~lit | prefix[i])
        if i + 1 < len(lits):
            m &= (~prefix[i] | prefix[i + 1])
            m &= (~lits[i + 1] | ~prefix[i])
    m &= functools.reduce(operator.or_, lits)
    return prefix


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

    # at[i][k] = city i is at place k of the trip (k = 0 is the start). The trip visits
    # every city once: each city has one place and each place has one city. This states
    # the trip directly as an order of the cities, which gives the solver stronger
    # propagation than only saying that every city is left and entered once.
    at = [m.bool_vector(f"at_{i}", n) for i in range(n)]
    city_before = []  # city_before[i][k] = city i is at one of the places 0..k
    for i in range(n):
        city_before.append(exactly_one(m, [at[i][k] for k in range(n)], f"city_{i}"))
    for k in range(n):
        exactly_one(m, [at[i][k] for i in range(n)], f"place_{k}")

    # The trip starts at city 0 (any trip can be started from any of its cities, so this
    # does not exclude a trip length).
    m &= at[0][0]

    # go[i][j] = the trip goes from city i directly to city j: city j is at the place
    # after the one of city i (the last place is followed by the first, the return to the
    # start). Stated in both directions.
    for i in range(n):
        m &= ~go[i][i]
        for j in range(n):
            if i != j:
                for k in range(n):
                    after = (k + 1) % n
                    m &= (~at[i][k] | ~at[j][after] | go[i][j])
                    m &= (~go[i][j] | ~at[i][k] | at[j][after])
    # Implied: every city is left once and entered once.
    for i in range(n):
        m &= go.row(i).exactly_one()
        m &= go.col(i).exactly_one()

    # Symmetry breaking (does not change the declared output, the trip length): when
    # distances are symmetric, a trip driven backwards has the same length, and it puts
    # city 1 after city 2 if it was before. Requiring city 1 to come before city 2
    # keeps one of the two directions.
    symmetric = all(distance[i][j] == distance[j][i] for i in range(n) for j in range(n))
    if symmetric and n > 3:
        for k in range(1, n):
            m &= (~at[2][k] | city_before[1][k - 1])

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

    # Minimise the length of the trip, which is the binary number just built. A soft clause
    # pays when its literal is false, so each bit of the length that is on pays its weight
    # 2^k through the negation of the bit. Every weight is more than all the lower ones
    # together, so the cheapest total is the smallest length. (Paying per leg instead gave
    # hundreds of soft clauses with many different weights, which the solver found slow.)
    for k, bit in enumerate(total):
        if bit is not None:
            m.obj[2 ** k] += ~bit

    return m, {"travel_distance": travel_distance}
