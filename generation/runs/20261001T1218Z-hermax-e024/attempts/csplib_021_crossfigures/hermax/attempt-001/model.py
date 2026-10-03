# Crossfigure (CSPLib 21): the numerical crossword. Fill the 9x9 grid with digits so that
# every across and down entry is the number its clue describes.
import functools
import itertools
import math
import operator

from hermax.model import Model

# The grid and the clues are fixed by the problem; the instance carries no data.
# Black squares (0-based row, column); they hold 0.
BLACK = [(0, 4), (1, 2), (1, 6), (2, 1), (2, 4), (2, 7), (4, 0), (4, 2), (4, 3), (4, 4),
         (4, 5), (4, 6), (4, 8), (6, 1), (6, 4), (6, 7), (7, 2), (7, 6)]
# entry name -> (length, row, column), 1-based as in the puzzle
ACROSS = {"A1": (4, 1, 1), "A4": (4, 1, 6), "A7": (2, 2, 1), "A8": (3, 2, 4), "A9": (2, 2, 8),
          "A10": (2, 3, 3), "A11": (2, 3, 6), "A13": (4, 4, 1), "A15": (4, 4, 6),
          "A17": (4, 6, 1), "A20": (4, 6, 6), "A23": (2, 7, 3), "A24": (2, 7, 6),
          "A25": (2, 8, 1), "A27": (3, 8, 4), "A28": (2, 8, 8), "A29": (4, 9, 1),
          "A30": (4, 9, 6)}
DOWN = {"D1": (4, 1, 1), "D2": (2, 1, 2), "D3": (4, 1, 4), "D4": (4, 1, 6), "D5": (2, 1, 8),
        "D6": (4, 1, 9), "D10": (2, 3, 3), "D12": (2, 3, 7), "D14": (3, 4, 2),
        "D16": (3, 4, 8), "D17": (4, 6, 1), "D18": (2, 6, 3), "D19": (4, 6, 4),
        "D20": (4, 6, 6), "D21": (2, 6, 7), "D22": (4, 6, 9), "D26": (2, 8, 2),
        "D28": (2, 8, 8)}


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


def is_one_of(m, bits, values, name):
    """Post: the binary number bits equals one of the constants in values."""
    choice = m.bool_vector(name, len(values))
    for c, value in zip(choice, values):
        if value >> len(bits):
            m &= ~c
            continue
        for k, bit in enumerate(bits):
            wanted = (value >> k) & 1
            if bit is None:
                if wanted:
                    m &= ~c
            else:
                m &= (~c | bit) if wanted else (~c | ~bit)
    m &= functools.reduce(operator.or_, list(choice))


def is_prime(v):
    return v >= 2 and all(v % d for d in range(2, math.isqrt(v) + 1))


def build(instance):
    n = 9

    m = Model()
    # M[i][j] = the digit in square (i, j); black squares hold 0
    M = m.int_matrix("M", n, n, 0, 9)
    for i, j in BLACK:
        m &= (M[i][j] == 0)

    # digit_bits[i][j][b] = bit b of the digit in square (i, j): the digit as a binary number,
    # so that the entries can be built with adder circuits (equalities between multi-digit
    # numbers posted on integer variables are expensive to encode here).
    digit_bits = [[m.bool_vector(f"bits_{i}_{j}", 4) for j in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(n):
            for v in range(10):
                for b in range(4):
                    bit = digit_bits[i][j][b] if (v >> b) & 1 else ~digit_bits[i][j][b]
                    m &= (~(M[i][j] == v) | bit)

    # An across entry is the number its digits spell left to right, a down entry top to bottom.
    def entry_terms(length, row, col, across):
        terms = []
        for p in range(length):
            i, j = (row - 1, col - 1 + p) if across else (row - 1 + p, col - 1)
            for b in range(4):
                terms.append((10 ** (length - 1 - p) * 2 ** b, digit_bits[i][j][b]))
        return terms

    terms = {}
    for name, (length, row, col) in ACROSS.items():
        terms[name] = entry_terms(length, row, col, True)
    for name, (length, row, col) in DOWN.items():
        terms[name] = entry_terms(length, row, col, False)
    value = {name: sum_bits(m, t) for name, t in terms.items()}

    true = m.bool("true")
    m &= true

    def number(*parts):
        """Bits of sum(c * entry) + constant, from parts that are (c, entry name) or an int."""
        items = []
        for part in parts:
            if isinstance(part, int):
                items += [(2 ** k, true) for k in range(part.bit_length()) if (part >> k) & 1]
            else:
                c, name = part
                items += [(c * w, lit) for w, lit in terms[name]]
        return sum_bits(m, items)

    def product(a, b):
        """Bits of entry a times entry b, as the sum of the partial products of their bits."""
        items = []
        for k, x in enumerate(value[a]):
            for l, y in enumerate(value[b]):
                if x is not None and y is not None:
                    items.append((2 ** (k + l), define(m, [x, y], lambda p, q: p & q)))
        return sum_bits(m, items)

    def equal(lhs, rhs):
        same_number(m, lhs, rhs)

    squares = [k * k for k in range(1, 101)]          # squares of up to four digits
    primes = [v for v in range(2, 100) if is_prime(v)]  # 23 across has two digits

    # Across
    equal(value["A1"], number((2, "A27")))                  # 1: 27 across times two
    equal(value["A4"], number((1, "D4"), 71))               # 4: 4 down plus seventy-one
    equal(value["A7"], number((1, "D18"), 4))               # 7: 18 down plus four
    equal(number((16, "A8")), value["D6"])                  # 8: 6 down divided by sixteen
    equal(number((1, "A9"), 18), value["D2"])               # 9: 2 down minus eighteen
    equal(number((12, "A10")), number(6 * 144))             # 10: dozen in six gross
    equal(number((1, "A11"), 70), value["D5"])              # 11: 5 down minus seventy
    equal(value["A13"], product("D26", "A23"))              # 13: 26 down times 23 across
    equal(number((1, "A15"), 350), value["D6"])             # 15: 6 down minus 350
    equal(value["A17"], product("A25", "A23"))              # 17: 25 across times 23 across
    is_one_of(m, value["A20"], squares, "A20_square")       # 20: a square number
    is_one_of(m, value["A23"], primes, "A23_prime")         # 23: a prime number
    is_one_of(m, value["A24"], squares, "A24_square")       # 24: a square number
    equal(number((17, "A25")), value["A20"])                # 25: 20 across divided by seventeen
    equal(number((4, "A27")), value["D6"])                  # 27: 6 down divided by four
    equal(value["A28"], number(4 * 12))                     # 28: four dozen
    equal(value["A29"], number(7 * 144))                    # 29: seven gross
    equal(value["A30"], number((1, "D22"), 450))            # 30: 22 down plus 450

    # Down
    equal(value["D1"], number((1, "A1"), 27))               # 1: 1 across plus twenty-seven
    equal(value["D2"], number(5 * 12))                      # 2: five dozen
    equal(value["D3"], number((1, "A30"), 888))             # 3: 30 across plus 888
    equal(value["D4"], number((2, "A17")))                  # 4: two times 17 across
    equal(number((12, "D5")), value["A29"])                 # 5: 29 across divided by twelve
    equal(value["D6"], product("A28", "A23"))               # 6: 28 across times 23 across
    equal(value["D10"], number((1, "A10"), 4))              # 10: 10 across plus four
    equal(value["D12"], number((3, "A24")))                 # 12: three times 24 across
    equal(number((16, "D14")), value["A13"])                # 14: 13 across divided by sixteen
    equal(value["D16"], number((15, "D28")))                # 16: 28 down times fifteen
    equal(number((1, "D17"), 399), value["A13"])            # 17: 13 across minus 399
    equal(number((18, "D18")), value["A29"])                # 18: 29 across divided by eighteen
    equal(number((1, "D19"), 94), value["D22"])             # 19: 22 down minus ninety-four
    equal(number((1, "D20"), 9), value["A20"])              # 20: 20 across minus nine
    equal(number((1, "D21"), 52), value["A25"])             # 21: 25 across minus fifty-two
    equal(value["D22"], number((6, "D20")))                 # 22: 20 down times six
    equal(value["D26"], number((5, "A24")))                 # 26: five times 24 across
    equal(value["D28"], number((1, "D21"), 27))             # 28: 21 down plus twenty-seven

    return m, {"M": M}
