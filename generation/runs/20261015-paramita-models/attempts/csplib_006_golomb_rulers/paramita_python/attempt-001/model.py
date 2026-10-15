from paramita.modelling import Bool, If, Iff, Or

# Golomb ruler with m marks: positions 0 = a_1 < a_2 < ... < a_m such that all
# pairwise differences are distinct. Minimise the length a_m.
#
# Positions are Bools b[p] over 0..L (true = a mark at p). The bound L is a domain bound
# derived here from the Erdos-Turan construction: for a prime p >= m, the marks
# 2*p*k + (k*k mod p), k = 0..m-1, form a Golomb ruler, so an optimal ruler fits within
# the length of that ruler.


def smallest_prime_at_least(n):
    p = max(n, 2)
    while any(p % f == 0 for f in range(2, int(p ** 0.5) + 1)):
        p += 1
    return p


def erdos_turan_length(m):
    p = smallest_prime_at_least(m)
    return max(2 * p * k + (k * k) % p for k in range(m))


def build(instance):
    m = instance["size"]
    L = erdos_turan_length(m)
    b = [Bool(f"b_{p}") for p in range(L + 1)]
    cons = []

    # the ruler starts at mark 0 and has exactly m marks
    cons.append(b[0])
    cons.append(sum(b) == m)

    # distinct differences: for each difference d, at most one pair of marks is d apart
    for d in range(1, L + 1):
        q = [Bool(f"q_{p}_{d}") for p in range(L + 1 - d)]
        for p in range(L + 1 - d):
            # a pair of marks at p and p+d forces the difference d to be used
            cons.append(If(b[p] & b[p + d], q[p]))
        cons.append(sum(q) <= 1)

    # unary count G[p+1][k] = "at least k marks lie in positions 0..p" (index shifted by one)
    G = [[Bool(f"g_{p}_{k}") for k in range(m + 1)] for p in range(L + 2)]
    for p in range(L + 2):
        cons.append(G[p][0])                      # zero marks: always true
    for k in range(1, m + 1):
        cons.append(~G[0][k])                     # no positions before 0: never true
    for p in range(L + 1):
        for k in range(1, m + 1):
            # the k-th mark is at or before p exactly when the count was already k,
            # or position p is a mark and the count before p was k - 1
            cons.append(Iff(G[p + 1][k], Or([G[p][k], b[p] & G[p][k - 1]])))

    # the k-th mark a_k is the number of positions whose count is still below k
    marks = [(L + 1) + sum(-1 * G[p + 1][k] for p in range(L + 1)) for k in range(1, m + 1)]
    length = marks[-1]
    return cons, {"length": length, "marks": marks}, ("minimize", length)
