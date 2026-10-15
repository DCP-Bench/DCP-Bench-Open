# A boy with some apples passes num_gates gates. At each gate the guard is paid
# half of his apples plus one. Apples must be whole, so each gate needs an even
# count: apples[i] == 2 * half[i]. After the last gate he has one apple left,
# which he gives the girl, leaving none.
# Integers are binary: value = sum(2**k * bit_k), with width W = num_gates + 2.
# W is safe: the chain is forced from apples[n] = 1 (apples[i] + 2 = 2*(apples[i+1] + 2)),
# so apples[0] = 3 * 2**n - 2 < 2**(n+2) and every apples[i] fits in n+2 bits.
from paramita.modelling import Bool


def build(instance):
    n = instance["num_gates"]
    W = n + 2
    cons = []

    def binary(name):
        bits = [Bool(f"{name}_bit_{k}") for k in range(W)]
        return bits, sum((2 ** k) * bits[k] for k in range(W))

    # apples he has before gate i+1 (i = 0..n-1), and after the last gate (i = n)
    apple_bits, apples = zip(*[binary(f"apples_{i}") for i in range(n + 1)])
    # apples he gives the guard at gate i+1 is half of his apples (integer), plus one
    half_bits, half = zip(*[binary(f"half_{i}") for i in range(n)])

    # the boy has no knife, so he gives a whole number of apples: apples before each gate are even
    for i in range(n):
        cons.append(apples[i] == 2 * half[i])

    # each guard gets half of his apples plus one, so apples after the gate are apples - half - 1
    for i in range(n):
        cons.append(apples[i + 1] + half[i] + 1 == apples[i])

    # after the last gate he has one apple, which he gives the girl, leaving none
    cons.append(apples[n] == 1)

    return cons, {"apples": list(apples)}
