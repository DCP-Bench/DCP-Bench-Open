# Ternary Steiner problem of order n: find n(n-1)/6 triples of distinct elements from
# {1, ..., n} such that any two triples have at most one common element.
# sets[i][j] = 1 if element j (0-based) is part of triple i.
import mip


def build(instance):
    n = instance["n"]
    num_triples = n * (n - 1) // 6
    model = mip.Model(solver_name="CBC")
    model.emphasis = 1

    # sets[i][j] = 1 if element j is part of triple i (binary decisions)
    sets = [
        [model.add_var(f"x_{i}_{j}", var_type=mip.BINARY) for j in range(n)]
        for i in range(num_triples)
    ]

    # each triple consists of exactly three distinct elements
    for i in range(num_triples):
        model.add_constr(mip.xsum(sets[i]) == 3, f"triple_{i}_size")

    # any two triples have at most one common element: every pair of elements {a, b}
    # lies in at most one triple. Counting gives n(n-1)/6 * 3 = n(n-1)/2 pairs in total,
    # so every pair lies in exactly one triple.
    # both[i][a][b] is continuous and only pushed up: both >= x_a + x_b - 1 means it
    # is 1 when both elements are in triple i. Its sum over triples is exactly 1.
    for a in range(n):
        for b in range(a + 1, n):
            both = []
            for i in range(num_triples):
                w = model.add_var(f"both_{i}_{a}_{b}", lb=0, ub=1, var_type=mip.CONTINUOUS)
                model.add_constr(w >= sets[i][a] + sets[i][b] - 1, f"both_{i}_{a}_{b}_ge")
                both.append(w)
            # two elements a and b occur together in exactly one triple
            model.add_constr(mip.xsum(both) == 1, f"pair_{a}_{b}_once")

    # implied by the pair condition: each element has n-1 partners, and each triple
    # containing it gives it 2 partners, so it lies in (n-1)/2 triples
    for j in range(n):
        model.add_constr(mip.xsum(sets[i][j] for i in range(num_triples)) == (n - 1) // 2,
                         f"element_{j}_degree")

    return model, {"sets": sets}
