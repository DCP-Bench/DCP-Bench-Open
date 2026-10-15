from paramita.modelling import Bool, Iff

# Autocorrelation (periodic): a binary sequence of length n with bits S_i in {+1, -1}
# minimising the sum of the squared periodic autocorrelations C_1..C_{n-1}.
# s_i is true when S_i = +1, so S_i = 2*s_i - 1.


def build(instance):
    n = instance["n"]
    s = [Bool(f"s_{i}") for i in range(n)]
    cons = []
    energy = 0

    for k in range(1, n):
        # the pair (S_i, S_((i+k) mod n)) differs; d[i] is true for each such i
        d = [Bool(f"d_{k}_{i}") for i in range(n)]
        for i in range(n):
            j = (i + k) % n
            cons.append(Iff(d[i], s[i] + s[j] == 1))

        # C_k = n - 2v, where v is the number of differing pairs; v is one-hot in e
        e = [Bool(f"e_{k}_{v}") for v in range(n + 1)]
        # the lag-k count takes exactly one value
        cons.append(sum(e) == 1)
        # the number of differing pairs equals that value
        cons.append(sum(d) == sum(v * e[v] for v in range(n + 1)))

        # energy: the sum of the squared autocorrelations C_k^2
        energy += sum((n - 2 * v) ** 2 * e[v] for v in range(n + 1))

    sequence = [2 * s[i] - 1 for i in range(n)]
    return cons, {"sequence": sequence}, ("minimize", energy)
