# Pythagorean triplet: find natural numbers a, b, c with a^2 + b^2 = c^2 and a + b + c = 1000.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine
from pysat.pb import PBEnc, EncType


def build(instance):
    total = 1000          # a + b + c has to equal this (given by the problem)
    low, high = 1, 500    # a, b and c are natural numbers; none can exceed half the total
    n_bits = high.bit_length()                # bits needed for a number 1..high
    n_square_bits = (high * high).bit_length()  # bits needed for its square

    pool = IDPool()
    numbers = {name: Integer(name, low, high, vpool=pool) for name in "abc"}
    engine = IntegerEngine(vars=list(numbers.values()), vpool=pool)
    cnf = engine.clausify()

    # PySAT cannot multiply two variables, so each number also gets its binary digits and the
    # binary digits of its square, tabulated value by value: choosing the value v fixes the bits
    # of v and of v * v. The two equations are then sums over these bits.
    value_bits, square_bits = {}, {}
    for name, x in numbers.items():
        value_bits[name] = [pool.id((name, "bit", k)) for k in range(n_bits)]
        square_bits[name] = [pool.id((name, "square_bit", k)) for k in range(n_square_bits)]
        for v in range(low, high + 1):
            for k in range(n_bits):
                bit = value_bits[name][k]
                cnf.append([-x.equals(v), bit if (v >> k) & 1 else -bit])
            for k in range(n_square_bits):
                bit = square_bits[name][k]
                cnf.append([-x.equals(v), bit if ((v * v) >> k) & 1 else -bit])

    # a + b + c == total, as a weighted sum of the binary digits
    cnf.extend(PBEnc.equals(
        lits=[bit for name in "abc" for bit in value_bits[name]],
        weights=[1 << k for name in "abc" for k in range(n_bits)],
        bound=total, vpool=pool, encoding=EncType.bdd).clauses)

    # a^2 + b^2 == c^2, i.e. a^2 + b^2 - c^2 == 0 over the binary digits of the squares. The
    # numbers are large (up to 2^18), so the adder encoding is used: a BDD over them would be huge.
    cnf.extend(PBEnc.equals(
        lits=[bit for name in "abc" for bit in square_bits[name]],
        weights=[(1 << k) * (-1 if name == "c" else 1) for name in "abc" for k in range(n_square_bits)],
        bound=0, vpool=pool, encoding=EncType.adder).clauses)

    return cnf, {name: numbers[name] for name in "abc"}
