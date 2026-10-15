# Equal-sized groups: split a sorted list of N elements into K contiguous groups,
# with K-1 split points, so that each group size is as close as possible to round(N/K).
# Equal values stay together, so a split point is never placed between two equal elements.
# N, K and the list come from the instance; the 1-based split points are the output x.
# Positions are binary (not one-hot or unary): N can be 1000, and a unary sum over that many
# Bools per size constraint ran out of memory.
from paramita.modelling import Bool, If, Or


def build(instance):
    a = instance["a"]
    n = len(a)
    k = instance["k"]
    ideal = round(n / k)  # round(N/K), the target group size

    # Split point j (1..K-1) is a position p_j in 1..N-1, written in binary bits.
    nbits = max(1, n.bit_length())
    pos_bits = {j: [Bool(f"split_{j}_bit_{b}") for b in range(nbits)] for j in range(1, k)}
    pos = {j: sum((1 << b) * pos_bits[j][b] for b in range(nbits)) for j in range(1, k)}

    cons = []
    # every split point lies inside the list: 1 <= p_j <= N-1
    for j in range(1, k):
        cons += [pos[j] >= 1, pos[j] <= n - 1]

    # groups are non-empty and ordered: p_j is at least one element after p_{j-1}
    for j in range(2, k):
        cons.append(pos[j] - pos[j - 1] >= 1)

    # items with the same value must be in the same group: no split point between equal neighbours.
    # A split at position i is p_j == i, so "not at i" is a clause over the bits of p_j.
    for j in range(1, k):
        for i in range(1, n):
            if a[i - 1] != a[i]:
                continue
            cons.append(Or([~bit if (i >> b) & 1 else bit for b, bit in enumerate(pos_bits[j])]))

    # group sizes: s_j = p_j - p_{j-1}, with p_0 = 0 and p_K = N
    def size_terms(j):
        terms = []
        if j <= k - 1:
            terms += [((1 << b), pos_bits[j][b]) for b in range(nbits)]
        if j >= 2:
            terms += [(-(1 << b), pos_bits[j - 1][b]) for b in range(nbits)]
        const = n if j == k else 0
        return terms, const

    # error bound: every group has between 1 and N-K+1 elements, so |s_j - round(N/K)| is bounded
    max_err = max(ideal - 1, n - k + 1 - ideal, 0)
    ebits = max(1, max_err.bit_length())
    err_bits = {j: [Bool(f"err_{j}_bit_{q}") for q in range(ebits)] for j in range(1, k + 1)}

    # |s_j - round(N/K)| <= e_j, as two PB constraints over the binary bits
    for j in range(1, k + 1):
        terms, const = size_terms(j)
        e_j = sum((1 << q) * err_bits[j][q] for q in range(ebits))
        # s_j - ideal <= e_j
        cons.append(sum(c * b for c, b in terms) - e_j <= ideal - const)
        # ideal - s_j <= e_j
        cons.append(-sum(c * b for c, b in terms) - e_j <= -ideal + const)

    # objective: total error, the sum of all e_j
    total_error = sum(sum((1 << q) * err_bits[j][q] for q in range(ebits)) for j in range(1, k + 1))

    # output: the 1-based split points
    x = [pos[j] for j in range(1, k)]

    return cons, {"x": x}, ("minimize", total_error)
