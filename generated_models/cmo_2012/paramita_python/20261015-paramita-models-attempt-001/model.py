"""CMO 2012: given positive integers a and b with a - b prime and a * b a
perfect square n^2, find the smallest a that is no less than min_a.
Print a, b, n and p, where p = a - b."""

from paramita.modelling import Bool, If, Iff


def primes_up_to(m):
    # the primes up to the instance bound: the candidate values of p
    sieve = [True] * (m + 1)
    result = []
    for k in range(2, m + 1):
        if sieve[k]:
            result.append(k)
            for multiple in range(k * k, m + 1, k):
                sieve[multiple] = False
    return result


def binary_number(name, bits):
    # a non-negative integer as bits with weights 1, 2, 4, ...
    B = [Bool(f"{name}_bit_{i}") for i in range(bits)]
    return B, sum((2 ** i) * B[i] for i in range(bits))


def unary_number(name, length):
    # an integer 0..length as a count of true Booleans u_1 >= u_2 >= ...
    U = [Bool(f"{name}_ge_{t}") for t in range(1, length + 1)]
    cons = [If(U[t + 1], U[t]) for t in range(length - 1)]
    return U, cons, sum(U)


def product_bits(name, X, Y):
    # the bits of X * Y, built column by column: the partial products X_i and Y_j
    # (weight 2^(i+j)) are summed per column together with the carry from the
    # column below, and the result bit of each column is what is left over.
    bits = len(X)
    width = 2 * bits
    cons = []
    result = []
    carry = None  # no carry into the lowest column
    for k in range(width):
        column = []
        for i in range(bits):
            j = k - i
            if 0 <= j < bits:
                t = Bool(f"{name}_pp_{i}_{j}")
                cons.append(Iff(t, X[i] & Y[j]))
                column.append(t)
        r = Bool(f"{name}_bit_{k}")
        result.append(r)
        # the carry out of this column, as a unary count up to the bit width
        out_u, out_cons, out_count = unary_number(f"{name}_carry_{k}", bits)
        cons += out_cons
        carry_in = 0 if carry is None else carry
        # column sum + carry in = result bit + 2 * carry out
        cons.append(sum(column) + carry_in == r + 2 * out_count)
        carry = out_count
    # nothing is left above the top column
    cons.append(carry == 0)
    return result, cons


def build(instance):
    min_a = instance["min_a"]
    max_val = instance["max_val"]
    bits = max_val.bit_length()

    A_bits, a = binary_number("a", bits)
    B_bits, b = binary_number("b", bits)
    N_bits, n = binary_number("n", bits)
    cons = []

    # a and b are positive integers no larger than the bound
    cons.append(b >= 1)
    cons.append(a <= max_val)
    cons.append(b <= max_val)
    cons.append(n <= max_val)

    # a is no less than the given minimum
    cons.append(a >= min_a)

    # a - b is a prime number: p is a binary number equal to one of the primes up to the bound
    P_bits, p = binary_number("p", bits)
    primes = primes_up_to(max_val)
    P = {q: Bool(f"p_is_{q}") for q in primes}
    cons.append(sum(P.values()) == 1)
    cons += [If(P[q], p == q) for q in primes]
    cons.append(p <= max_val)
    cons.append(a - b == p)

    # a * b is a perfect square n^2: the two products have equal bits
    ab_bits, ab_cons = product_bits("ab", A_bits, B_bits)
    nn_bits, nn_cons = product_bits("nn", N_bits, N_bits)
    cons += ab_cons + nn_cons
    cons += [Iff(x, y) for x, y in zip(ab_bits, nn_bits)]

    return cons, {"a": a, "b": b, "n": n, "p": p}, ("minimize", a)
