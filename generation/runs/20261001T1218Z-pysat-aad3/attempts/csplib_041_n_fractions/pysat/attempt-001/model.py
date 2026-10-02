# N fractions (CSPLib 41): find distinct non-zero digits A..I such that
# A / BC + D / EF + G / HI = 1, where BC, EF and HI are the two-digit numbers formed by the
# digits B and C, E and F, H and I.
from math import gcd

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    n = 9  # the digits are 1..9 (given by the problem)

    pool = IDPool()
    # digits = the nine digits A, B, C, D, E, F, G, H, I
    digits = [Integer(name, 1, n, vpool=pool) for name in "ABCDEFGHI"]
    A, B, C, D, E, F, G, H, I = digits
    # D1, D2, D3 = the two-digit numbers BC, EF, HI. The reference bounds them by n * n = 81.
    D1, D2, D3 = (Integer(f"D{k}", 1, n * n, vpool=pool) for k in (1, 2, 3))
    engine = IntegerEngine(vars=digits + [D1, D2, D3], vpool=pool)

    # all nine digits are different
    engine.add_alldifferent(digits)

    # each two-digit number is ten times its first digit plus its second digit
    engine.add_linear(D1 == 10 * B + C)
    engine.add_linear(D2 == 10 * E + F)
    engine.add_linear(D3 == 10 * H + I)

    cnf = engine.clausify()

    # The equation A/D1 + D/D2 + G/D3 = 1, read as: the first two fractions add up to what is left
    # of 1 after the third. PySAT cannot divide or multiply variables, so each fraction is
    # tabulated by its numerator and denominator: is_fraction[k][(num, den)] is a literal that
    # must be true whenever the k-th fraction is num / den.
    fractions = [(A, D1), (D, D2), (G, D3)]
    is_fraction = []
    for numerator, denominator in fractions:
        table = {}
        for num in range(1, n + 1):
            for den in range(1, n * n + 1):
                literal = pool.id(("fraction", numerator.name, num, den))
                cnf.append([-numerator.equals(num), -denominator.equals(den), literal])
                table[(num, den)] = literal
        is_fraction.append(table)

    def reduced(num, den):
        g = gcd(num, den)
        return (num // g, den // g)

    # remainder_is[v] stands for "1 minus the third fraction equals v" (v as a reduced fraction).
    # Every third fraction forces the literal of its remainder, and at most one such literal may
    # hold.
    remainder_is = {}
    for (num, den), literal in is_fraction[2].items():
        remainder = reduced(den - num, den)
        if remainder not in remainder_is:
            remainder_is[remainder] = pool.id(("remainder", remainder))
        cnf.append([-literal, remainder_is[remainder]])
    cnf.extend(CardEnc.atmost(lits=list(remainder_is.values()), bound=1, vpool=pool,
                              encoding=EncType.seqcounter).clauses)

    # The first two fractions add up to a value; it has to be the remainder. A pair of fractions
    # whose sum is not a remainder that some third fraction leaves is ruled out.
    for (num1, den1), first in is_fraction[0].items():
        for (num2, den2), second in is_fraction[1].items():
            total = reduced(num1 * den2 + num2 * den1, den1 * den2)
            if total in remainder_is:
                cnf.append([-first, -second, remainder_is[total]])
            else:
                cnf.append([-first, -second])

    return cnf, {name: digit for name, digit in zip("ABCDEFGHI", digits)}
