# 2012 Canadian Mathematical Olympiad problem: find positive integers a and b
# such that a - b is a prime p and a * b is a perfect square n^2, with a as
# small as possible but no less than a given minimum.
#
# PySAT has no integer multiplication, so a, b, n and p are written in binary
# (one literal per bit) and the arithmetic is built from adder and
# multiplier circuits in plain clauses. The four declared outputs are
# pysat.integer.Integer variables whose value literals are channelled to
# those bits.
from math import sqrt

from pysat.formula import IDPool, WCNF
from pysat.integer import Integer


def build(instance):
    min_a = instance["min_a"]
    max_val = instance["max_val"]

    pool = IDPool()
    formula = WCNF()
    true = pool.id("true")
    formula.append([true])
    false = -true

    # Every variable is at most max_val, so this many bits hold any of them.
    width = max(max_val.bit_length(), 2)

    def bits(name):
        return [pool.id((name, k)) for k in range(width)]

    def gate_and(x, y):
        z = pool.id()
        formula.extend([[-z, x], [-z, y], [z, -x, -y]])
        return z

    def full_adder(x, y, c):
        # s = x xor y xor c, carry = majority(x, y, c), both directions.
        s, carry = pool.id(), pool.id()
        for vx in (True, False):
            for vy in (True, False):
                for vc in (True, False):
                    odd = vx ^ vy ^ vc
                    formula.append([-x if vx else x, -y if vy else y,
                                    -c if vc else c, s if odd else -s])
        formula.extend([[-x, -y, carry], [-x, -c, carry], [-y, -c, carry],
                        [x, y, -carry], [x, c, -carry], [y, c, -carry]])
        return s, carry

    def add(xs, ys):
        # Ripple-carry sum of two bit vectors; one bit longer than the longer.
        length = max(len(xs), len(ys))
        xs = xs + [false] * (length - len(xs))
        ys = ys + [false] * (length - len(ys))
        out, carry = [], false
        for x, y in zip(xs, ys):
            s, carry = full_adder(x, y, carry)
            out.append(s)
        return out + [carry]

    def multiply(xs, ys):
        # Shift-and-add: add up x * (bit j of y) * 2^j over every bit j.
        total = [false]
        for j, y in enumerate(ys):
            row = [false] * j + [gate_and(x, y) for x in xs]
            total = add(total, row)
        return total

    def same(xs, ys):
        # Two bit vectors denote the same number.
        length = max(len(xs), len(ys))
        xs = xs + [false] * (length - len(xs))
        ys = ys + [false] * (length - len(ys))
        for x, y in zip(xs, ys):
            formula.extend([[-x, y], [x, -y]])

    def at_most(xs, c):
        # xs <= c: forbid every bit where xs has a 1, c has a 0, and all
        # higher bits agree with c.
        for k in range(len(xs)):
            if not (c >> k) & 1:
                clause = [-xs[k]]
                for j in range(k + 1, len(xs)):
                    clause.append(-xs[j] if (c >> j) & 1 else xs[j])
                formula.append(clause)

    def at_least(xs, c):
        # xs >= c: forbid every bit where xs has a 0, c has a 1, and all
        # higher bits agree with c.
        for k in range(len(xs)):
            if (c >> k) & 1:
                clause = [xs[k]]
                for j in range(k + 1, len(xs)):
                    clause.append(-xs[j] if (c >> j) & 1 else xs[j])
                formula.append(clause)

    a, b, n, p = bits("a"), bits("b"), bits("n"), bits("p")

    # Domains, as in the reference: min_a <= a <= max_val, 1 <= b <= max_val,
    # 0 <= n <= max_val.
    at_least(a, min_a)
    at_most(a, max_val)
    at_least(b, 1)
    at_most(b, max_val)
    at_most(n, max_val)

    # p is a prime below max_val (the reference's prime list): every other
    # value p's bits can spell is forbidden, which also keeps 2 <= p.
    def is_prime(v):
        if v < 2:
            return False
        return all(v % i for i in range(2, int(sqrt(v)) + 1))

    for v in range(1 << width):
        if not (v < max_val and is_prime(v)):
            formula.append([-p[k] if (v >> k) & 1 else p[k] for k in range(width)])

    # p = a - b, stated as a = b + p; since p >= 0 this also gives a >= b.
    same(add(b, p), a)

    # a * b is the perfect square n * n.
    same(multiply(a, b), multiply(n, n))

    # Implied: b <= a and a * b = n^2 give b^2 <= n^2 <= a^2, so b <= n <= a.
    # Stated as n = b + d1 and a = n + d2 with d1, d2 >= 0; it cuts no
    # solution and lets the solver prune before the multipliers decide.
    same(add(b, bits("d1")), n)
    same(add(n, bits("d2")), a)

    # Declared outputs: one Integer per variable, direct encoding over the
    # reference's domain, each value literal true exactly when the bits spell
    # that value. The bits take exactly one value, so the value literals need
    # no exactly-one constraint of their own.
    def as_integer(name, xs, lb, ub):
        var = Integer(name, lb, ub, vpool=pool)
        for v in range(lb, ub + 1):
            lit = var.equals(v)
            spelled = [xs[k] if (v >> k) & 1 else -xs[k] for k in range(width)]
            for s in spelled:
                formula.append([-lit, s])
            formula.append([lit] + [-s for s in spelled])
        return var

    outputs = {
        "a": as_integer("a", a, min_a, max_val),
        "b": as_integer("b", b, 1, max_val),
        "n": as_integer("n", n, 0, max_val),
        "p": as_integer("p", p, 2, max_val),
    }

    # Minimise a: bit k of a pays 2^k when set, so the falsified weight is a.
    for k in range(width):
        formula.append([-a[k]], weight=1 << k)

    return formula, outputs
