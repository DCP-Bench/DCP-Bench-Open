# Template design: a printing firm must print n_var variations of a product in given
# quantities (demand). Each template has n_slots slots, filled with copies of the
# variations, and a template that is used for `production` sheets prints every copy on
# it once per sheet. Decide the layout of each template and how many sheets are printed
# from it so that every variation reaches its demand, using as few sheets in all as
# possible.
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


def contradiction(m):
    """Make the model unsatisfiable."""
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


def bits_at_least(m, bits, value):
    """The literal "the binary number bits is at least value", or True / False when that
    is already settled. The comparison is built from the top bit down."""
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

    return at_least(len(bits), value)


def post_true(m, lit):
    """Post that a literal, or True / False, holds."""
    if lit is True:
        return
    if lit is False:
        contradiction(m)
    else:
        m &= lit


def negate(lit):
    """The negation of a literal or of True / False."""
    return (not lit) if isinstance(lit, bool) else ~lit


def post_at_most(m, xs, ys):
    """Post that the binary number xs is at most the binary number ys (lists of literals,
    least significant bit first, None for a bit that is always 0). Going from the lowest
    bit up, "the lower bits of xs are at most those of ys" holds after a bit if x < y at
    that bit, or x = y there and it held before."""
    holds = True
    for k in range(max(len(xs), len(ys))):
        x = xs[k] if k < len(xs) and xs[k] is not None else False
        y = ys[k] if k < len(ys) and ys[k] is not None else False
        smaller = literal_and(m, negate(x), y)
        same = literal_or(m, literal_and(m, x, y), literal_and(m, negate(x), negate(y)))
        holds = literal_or(m, smaller, literal_and(m, same, holds))
    post_true(m, holds)


def build(instance):
    n_slots = instance["n_slots"]  # slots on a template
    n_templates = instance["n_templates"]  # number of templates
    n_var = instance["n_var"]  # number of variations
    demand = instance["demand"]  # demand[v] = sheets' worth of copies variation v needs

    # The reference limits the sheets printed from a template to the largest demand and
    # the copies of one variation on a template to n_var (no template has more slots
    # than copies it could hold, so this is also at most n_slots).
    upper = max(demand)
    most_copies = min(n_var, n_slots)
    sheet_width = upper.bit_length()
    copy_width = max(1, most_copies.bit_length())

    m = Model()
    # The sheets printed from a template and the copies of a variation on it are written
    # in binary, which turns the products "sheets * copies" in the demand constraint
    # into sums of single bits; hermax has no cheap product of two wide integers.
    # sheet_bits[t][k] = the bit worth 2^k of the sheets printed from template t
    sheet_bits = [m.bool_vector(f"sheet_bits_{t}", sheet_width) for t in range(n_templates)]
    # copy_bits[t][v][j] = the bit worth 2^j of the copies of variation v on template t
    copy_bits = [[m.bool_vector(f"copy_bits_{t}_{v}", copy_width) for v in range(n_var)]
                 for t in range(n_templates)]
    # production[t] = sheets printed from template t, layout[t][v] = copies of variation v
    # on template t (the declared outputs), tied to their bits
    production = [integer_from_bits(m, list(sheet_bits[t]), f"production_{t}") for t in range(n_templates)]
    layout = [[integer_from_bits(m, list(copy_bits[t][v]), f"layout_{t}_{v}") for v in range(n_var)]
              for t in range(n_templates)]

    # at least one sheet and at most upper sheets are printed from a template
    for t in range(n_templates):
        m &= (production[t] >= 1)
        if upper + 1 < 2 ** sheet_width:
            m &= ~(production[t] >= upper + 1)
    # a variation has at most most_copies copies on a template
    for t in range(n_templates):
        for v in range(n_var):
            if most_copies + 1 < 2 ** copy_width:
                m &= ~(layout[t][v] >= most_copies + 1)

    # every slot of a template is filled: the copies on a template add up to n_slots
    # (adder circuits over the bits, fixed to n_slots)
    for t in range(n_templates):
        copies = sum_bits(m, [(2 ** j, copy_bits[t][v][j]) for v in range(n_var) for j in range(copy_width)])
        fix_bits(m, copies, n_slots)

    # Demand: the copies of variation v, over all templates, printed over all the sheets
    # of their template, reach demand[v]: sum over t of production[t] * layout[t][v].
    # A product of bit k of the sheets and bit j of the copies is worth 2^(j+k) and is on
    # exactly when both bits are.
    printed = []  # printed[v] = copies of variation v printed, as a binary number
    for v in range(n_var):
        terms = []
        for t in range(n_templates):
            for j in range(copy_width):
                for k in range(sheet_width):
                    both_on = m.bool()
                    m &= (~both_on | copy_bits[t][v][j])
                    m &= (~both_on | sheet_bits[t][k])
                    m &= (both_on | ~copy_bits[t][v][j] | ~sheet_bits[t][k])
                    terms.append((2 ** (j + k), both_on))
        printed.append(sum_bits(m, terms))
        post_true(m, bits_at_least(m, printed[v], demand[v]))

    # Implied (stated by the reference): every template fills all its slots, so the
    # sheets printed must cover the total demand: n_slots * total sheets >= total demand.
    total_sheets = sheet_bits[0]
    for t in range(1, n_templates):
        total_sheets = add_bits(m, total_sheets, sheet_bits[t])
    post_true(m, bits_at_least(m, total_sheets, -(-sum(demand) // n_slots)))

    # Implied (derived here): every sheet prints exactly n_slots copies, so the copies of all
    # variations printed add up to n_slots * total sheets. Every variation reaches its
    # demand, so the copies of variation v printed are at most n_slots * total sheets minus
    # the demand of the other variations. When the total is close to the smallest possible,
    # this leaves each variation almost no surplus, which is what the solver needs to see.
    capacity_bits = sum_bits(m, [(n_slots * 2 ** k, bit) for k, bit in enumerate(total_sheets)
                                 if bit is not None])
    always = m.bool()  # a literal fixed to true, for the bits of a constant
    m &= always
    for v in range(n_var):
        others = sum(demand) - demand[v]
        if others > 0:
            offset = [always if (others >> k) & 1 else None for k in range(others.bit_length())]
            post_at_most(m, add_bits(m, printed[v], offset), capacity_bits)

    # Minimise the sheets printed in all, the binary number total_sheets. A soft clause pays
    # when its literal is false, so each bit that is on pays its weight 2^k through the
    # negation of the bit. Every weight is more than all the lower ones together, so the
    # cheapest total is the smallest number of sheets.
    for k, bit in enumerate(total_sheets):
        if bit is not None:
            m.obj[2 ** k] += ~bit

    return m, {"production": production, "layout": layout}
