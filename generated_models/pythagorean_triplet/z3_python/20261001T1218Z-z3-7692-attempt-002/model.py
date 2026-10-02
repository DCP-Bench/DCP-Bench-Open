# Pythagorean triplet (Project Euler 9): find natural numbers a, b, c with
# a^2 + b^2 = c^2 and a + b + c = 1000.
import z3


def build(instance):
    del instance  # the puzzle states its own sum

    total = 1000        # the triplet sums to 1000
    largest = total // 2  # no side of a triangle reaches half the perimeter

    # Bit-vector encoding: squares are bit-blasted to SAT; Z3's nonlinear integer
    # arithmetic did not finish proving that no further triplet exists.
    bits = largest.bit_length()   # bits for a value up to 500
    square_bits = 2 * bits + 1    # bits for a sum of two squares
    sum_bits = bits + 2           # bits for a sum of three values

    a, b, c = (z3.BitVec(name, bits) for name in "abc")

    def square(v):
        wide = z3.ZeroExt(square_bits - bits, v)
        return wide * wide

    solver = z3.Solver()

    # Natural numbers, none larger than half the sum.
    for v in (a, b, c):
        solver.add(z3.UGE(v, 1), z3.ULE(v, largest))

    # The three numbers add up to 1000 (widened so the sum cannot wrap around).
    solver.add(z3.ZeroExt(sum_bits - bits, a) + z3.ZeroExt(sum_bits - bits, b)
               + z3.ZeroExt(sum_bits - bits, c) == total)

    # They form a Pythagorean triplet.
    solver.add(square(a) + square(b) == square(c))

    return solver, {"a": z3.BV2Int(a), "b": z3.BV2Int(b), "c": z3.BV2Int(c)}
