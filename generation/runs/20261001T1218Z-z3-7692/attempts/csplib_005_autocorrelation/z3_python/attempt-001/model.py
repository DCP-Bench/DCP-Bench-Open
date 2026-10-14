# Low autocorrelation binary sequences: choose a sequence of n values, each +1
# or -1, that minimises the sum of the squared periodic autocorrelations.
import z3


def build(instance):
    n = instance["n"]  # length of the sequence

    # sequence[i] is the i-th bit of the sequence, either -1 or +1.
    sequence = [z3.Int(f"sequence_{i}") for i in range(n)]

    solver = z3.Solver()

    # Each bit is -1 or +1 (0 is excluded).
    for bit in sequence:
        solver.add(z3.Or(bit == -1, bit == 1))

    # The periodic autocorrelation at shift k is the sum over i of
    # sequence[i] * sequence[(i + k) mod n]. Each product of two bits is +1 when they
    # are equal and -1 otherwise; writing it with If avoids a product of two
    # variables, which Z3 handles badly.
    # Each C_k lies between -n and n, so its square is looked up from a small table
    # instead of multiplying C_k by itself.
    squares = []
    for k in range(1, n):
        correlation = z3.Int(f"correlation_{k}")
        square = z3.Int(f"square_{k}")
        solver.add(correlation == z3.Sum([z3.If(sequence[i] == sequence[(i + k) % n], 1, -1)
                                          for i in range(n)]))
        solver.add(z3.Or([z3.And(correlation == v, square == v * v) for v in range(-n, n + 1)]))
        squares.append(square)

    # Energy E: the sum of the squared autocorrelations over shifts 1..n-1, minimised.
    energy = z3.Sum(squares)
    return solver, {"sequence": sequence}, ("minimize", energy)
