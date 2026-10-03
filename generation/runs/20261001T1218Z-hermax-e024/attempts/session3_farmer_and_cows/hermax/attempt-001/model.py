# Farmer and cows: a farmer has cows numbered 1 up to num_cows, and each cow gives as
# much milk as its number. He gives every son a fixed number of cows so that all sons
# receive the same total quantity of milk. Find which son gets which cow.

def contradiction(m):
    """Make the model unsatisfiable (used when a sum can never reach its required value)."""
    never = m.bool()
    m &= never
    m &= ~never


def fix_bits(m, bits, value):
    """Post that a binary number (list of literals, least significant bit first, None
    for a bit that is always 0) equals the constant value."""
    if value >> len(bits):  # the value needs more bits than the number can ever have
        contradiction(m)
    for k, bit in enumerate(bits):
        wanted = (value >> k) & 1
        if bit is None:
            if wanted:
                contradiction(m)
        else:
            m &= bit if wanted else ~bit
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
    num_cows = instance["num_cows"]  # cows are numbered 1..num_cows
    num_sons = instance["num_sons"]  # sons are numbered 0..num_sons-1
    cows_per_son = instance["cows_per_son"]  # cows_per_son[s] = number of cows son s gets

    # Cow i (counting from 0) is cow number i + 1 and gives i + 1 units of milk. The
    # reference gives every son total milk // num_sons.
    milk_per_cow = list(range(1, num_cows + 1))
    total_milk_per_son = sum(milk_per_cow) // num_sons

    m = Model()
    # gets[i][s] = cow i goes to son s
    gets = m.bool_matrix("gets", num_cows, num_sons)
    # cow_assignments[i] = the son that gets cow i (the declared output). hermax needs
    # at least two values, so with one son the second value is ruled out.
    cow_assignments = [m.int(f"cow_assignments_{i}", 0, max(num_sons - 1, 1)) for i in range(num_cows)]
    if num_sons == 1:
        for i in range(num_cows):
            m &= ~(cow_assignments[i] >= 1)

    # every cow goes to exactly one son
    for i in range(num_cows):
        m &= gets.row(i).exactly_one()
    # cow_assignments shows the son: going to son s means cow_assignments >= s and not
    # cow_assignments >= s + 1 (comparisons outside the range 0..num_sons-1 are settled)
    for i in range(num_cows):
        for s in range(num_sons):
            if s > 0:
                m &= (~gets[i][s] | (cow_assignments[i] >= s))
            if s < num_sons - 1:
                m &= (~gets[i][s] | ~(cow_assignments[i] >= s + 1))

    for s in range(num_sons):
        # each son gets his given number of cows
        m &= (sum(1 * gets[i][s] for i in range(num_cows)) == cows_per_son[s])
        # every son gets the same total milk. The milk of son s, the sum of the numbers
        # of his cows, is built as a binary number with adder circuits and fixed to the
        # shared total (a pseudo-Boolean equality over the whole range of the sum is the
        # expensive shape in hermax).
        milk = sum_bits(m, [(milk_per_cow[i], gets[i][s]) for i in range(num_cows)])
        fix_bits(m, milk, total_milk_per_son)

    return m, {"cow_assignments": cow_assignments}
