"""Low autocorrelation binary sequence (periodic): find a sequence of n bits, each
+1 or -1, that minimises the sum of the squares of its periodic autocorrelations.

The k-th periodic autocorrelation is C_k = sum over i of S[i] * S[(i + k) mod n],
and the energy to minimise is E = sum over k = 1..n-1 of C_k^2.
"""
import pulp


def build(instance):
    n = instance["n"]  # length of the sequence

    problem = pulp.LpProblem("autocorrelation", pulp.LpMinimize)

    # bit[i] = 1 if S[i] = +1 and 0 if S[i] = -1
    bit = [pulp.LpVariable(f"bit_{i}", cat="Binary") for i in range(n)]

    # sequence[i] = S[i], +1 or -1 (declared output); 0 is excluded because it is
    # built from a 0/1 variable as 2*bit - 1
    sequence = [2 * bit[i] - 1 for i in range(n)]

    # differ[i][j] = 1 if the bits at positions i and j differ, for i < j. The product
    # S[i] * S[j] is +1 when they agree and -1 when they differ, so it is
    # 1 - 2 * differ[i][j]. (Exclusive-or of two binaries, four rows.)
    differ = {}
    for i in range(n):
        for j in range(i + 1, n):
            d = pulp.LpVariable(f"differ_{i}_{j}", cat="Binary")
            problem += d >= bit[i] - bit[j]
            problem += d >= bit[j] - bit[i]
            problem += d <= bit[i] + bit[j]
            problem += d <= 2 - bit[i] - bit[j]
            differ[(i, j)] = d

    # C[k] = the k-th periodic autocorrelation, summing S[i] * S[(i + k) mod n]
    # over all i: n terms, each 1 - 2 * differ
    energy_terms = []
    for k in range(1, n):
        pairs = [differ[(min(i, (i + k) % n), max(i, (i + k) % n))] for i in range(n)]
        # an integer in n - 2*[0..n], so it has the parity of n
        C = pulp.LpVariable(f"C_{k}", -n, n, cat="Integer")
        problem += C == n - 2 * pulp.lpSum(pairs)

        # square[k] = C[k]^2. The square is convex, so under minimisation it is
        # enough to bound it below by its tangent line 2*v*C - v^2 at every value v
        # that C can take (parity of n, between -n and n); at those values the
        # largest tangent is exactly v^2.
        square = pulp.LpVariable(f"square_{k}", 0, n * n)
        for v in range(-n, n + 1):
            if (v - n) % 2 == 0:
                problem += square >= 2 * v * C - v * v
        energy_terms.append(square)

    # objective: minimise the energy, the sum of the squared autocorrelations
    problem += pulp.lpSum(energy_terms)

    return problem, {"sequence": sequence}
