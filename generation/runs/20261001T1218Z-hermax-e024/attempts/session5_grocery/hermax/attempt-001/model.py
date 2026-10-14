# Grocery: a kid buys num_items items and the cashier adds their prices (in cents) to
# get total_price. Multiplying the prices instead gives the same total once the product
# is scaled from cents to dollars (divided by 100 for every price after the first).
# Find the prices of the items, in cents.

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


def prime_exponents(n):
    """{prime: exponent} of the positive integer n, by trial division."""
    found = {}
    p = 2
    while p * p <= n:
        while n % p == 0:
            found[p] = found.get(p, 0) + 1
            n //= p
        p += 1
    if n > 1:
        found[n] = found.get(n, 0) + 1
    return found
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
    total_price = instance["total_price"]  # sum of the prices, in cents
    num_items = instance["num_items"]  # number of items bought

    # The prices (in cents) multiply to total_price * 100^(num_items - 1). A product of
    # integers cannot be written directly over wide integer variables in hermax, so the
    # product is handled through prime factors. Every price divides the product, so a
    # price is a divisor of it, and the product equals the target exactly when, for every
    # prime, the exponents of that prime in the prices add up to its exponent in the
    # target (unique factorisation).
    exponent = prime_exponents(total_price)
    for p in (2, 5):  # 100 = 2^2 * 5^2
        exponent[p] = exponent.get(p, 0) + 2 * (num_items - 1)
    divisors = [1]
    for p, e in exponent.items():
        divisors = [d * p ** k for d in divisors for k in range(e + 1)]
    # a price is between 1 and total_price, as the reference's variables are
    divisors = sorted(d for d in divisors if d <= total_price)
    if not divisors:
        raise ValueError("total_price must be at least 1")

    m = Model()
    # pick[i][k] = item i costs divisors[k] cents
    pick = m.bool_matrix("pick", num_items, len(divisors))
    # prices[i] = price of item i in cents (the declared output); a range of one value
    # is not an integer variable in hermax, so it gets a spare value that is ruled out
    prices = [m.int(f"prices_{i}", 1, max(total_price, 2)) for i in range(num_items)]
    if total_price < 2:
        for i in range(num_items):
            m &= ~(prices[i] >= 2)

    # every item has exactly one price
    for i in range(num_items):
        m &= pick.row(i).exactly_one()
    # prices shows the price chosen: price d means prices >= d and not prices >= d + 1
    for i in range(num_items):
        for k, d in enumerate(divisors):
            if d > 1:
                m &= (~pick[i][k] | (prices[i] >= d))
            if d < total_price:
                m &= (~pick[i][k] | ~(prices[i] >= d + 1))

    # The prices add up to total_price. Bit b of the price of item i is on when the
    # chosen divisor has bit b on; the prices are then added as binary numbers with
    # adder circuits and the sum is fixed to total_price.
    width = total_price.bit_length()
    price_bits = []
    for i in range(num_items):
        bits = []
        for b in range(width):
            having = [pick[i][k] for k, d in enumerate(divisors) if (d >> b) & 1]
            if not having:
                bits.append(None)
                continue
            bit = m.bool()
            m &= (~bit | functools.reduce(operator.or_, having))
            for lit in having:
                m &= (~lit | bit)
            bits.append(bit)
        price_bits.append(bits)
    total_bits = price_bits[0]
    for bits in price_bits[1:]:
        total_bits = add_bits(m, total_bits, bits)
    fix_bits(m, total_bits, total_price)

    # The prices multiply to the target: for every prime p, the exponents of p in the
    # prices add up to the exponent of p in the target. has[i][t] says the price of item
    # i is divisible by p^t; the exponent of p in a price is the number of t >= 1 for
    # which that holds, so these literals are counted.
    for p, e in exponent.items():
        counted = []
        for i in range(num_items):
            for t in range(1, e + 1):
                divisible = [pick[i][k] for k, d in enumerate(divisors) if d % p ** t == 0]
                if not divisible:
                    continue
                has = m.bool()
                m &= (~has | functools.reduce(operator.or_, divisible))
                for lit in divisible:
                    m &= (~lit | has)
                counted.append(has)
        if counted:
            m &= (sum(1 * lit for lit in counted) == e)
        else:
            contradiction(m)

    return m, {"prices": prices}
