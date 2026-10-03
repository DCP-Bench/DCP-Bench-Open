# Curious set of integers (Gardner): 1, 3, 8 and 120 have the property that the product of
# any two of them is one less than a perfect square. Extend the set to n numbers (between 0
# and max_val, all different) without losing the property, and report the last one.
import functools
import itertools
import math
import operator

from hermax.model import Model

# the four numbers of the set, fixed by the problem
GIVEN = [1, 3, 8, 120]


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


def same_number(m, xs, ys):
    """Post: the binary numbers xs and ys (None for an always-0 bit) are equal."""
    for k in range(max(len(xs), len(ys))):
        p = xs[k] if k < len(xs) else None
        q = ys[k] if k < len(ys) else None
        if p is None and q is None:
            continue
        if p is None:
            m &= ~q
        elif q is None:
            m &= ~p
        else:
            m &= (~p | q)
            m &= (p | ~q)


def at_most(m, bits, bound):
    """Post: the binary number bits is at most the constant bound. For every bit k where the
    bound has a 0, bit k may only be set if a higher bit where the bound has a 1 is off."""
    for k, bit in enumerate(bits):
        if bit is not None and not (bound >> k) & 1:
            higher = [~bits[j] for j in range(k + 1, len(bits)) if (bound >> j) & 1]
            m &= functools.reduce(operator.or_, [~bit] + higher)


def build(instance):
    n = instance["n"]              # size of the extended set
    max_val = instance["max_val"]  # every number, and every square root, is at most this

    m = Model()
    width = max_val.bit_length()
    true = m.bool("true")
    m &= true

    # unknown[k] = the k-th number added to the set; the last one is reported
    unknown = [m.int(f"x_{k}", 0, max_val) for k in range(n - len(GIVEN))]
    # bits[k] = unknown[k] as a binary number (least significant bit first): the products
    # below are built as binary circuits, since a product of integer variables equal to a
    # square has no direct linear form
    bits = [m.bool_vector(f"bits_{k}", width) for k in range(len(unknown))]
    for x, xb in zip(unknown, bits):
        for v in range(max_val + 1):
            for b in range(width):
                m &= (~(x == v) | (xb[b] if (v >> b) & 1 else ~xb[b]))

    # all numbers of the set are different
    if len(unknown) > 1:
        m &= m.vector(unknown).all_different()
    for x in unknown:
        for c in GIVEN:
            if c <= max_val:
                m &= (x != c)

    # numbers as (constant or None, bits or None)
    members = [(c, None) for c in GIVEN] + [(None, list(xb)) for xb in bits]

    def product_plus_one(a, b):
        (ca, ba), (cb, bb) = a, b
        if ba is None and bb is None:
            return None
        terms = [(1, true)]
        if ba is None or bb is None:
            c, xb = (ca, bb) if ba is None else (cb, ba)
            terms += [(c * 2 ** k, xb[k]) for k in range(width) if c > 0]
        else:
            terms += [(2 ** (k + l), define(m, [ba[k], bb[l]], lambda p, q: p & q))
                      for k in range(width) for l in range(width)]
        return sum_bits(m, terms)

    # The product of any two numbers of the set is one less than a perfect square whose root
    # is between 0 and max_val.
    for i, j in itertools.combinations(range(n), 2):
        target = product_plus_one(members[i], members[j])
        if target is None:
            # two numbers of the given set: a fact to check, not a constraint
            value = members[i][0] * members[j][0] + 1
            root = math.isqrt(value)
            if root * root != value or root > max_val:
                m &= (true & ~true)
            continue
        root = m.bool_vector(f"root_{i}_{j}", width)
        at_most(m, list(root), max_val)
        square = sum_bits(m, [(2 ** (k + l), define(m, [root[k], root[l]], lambda p, q: p & q))
                              for k in range(width) for l in range(width)])
        same_number(m, square, target)

    return m, {"number": unknown[-1]}
