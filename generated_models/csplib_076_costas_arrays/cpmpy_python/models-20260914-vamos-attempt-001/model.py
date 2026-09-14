import cpmpy as cp


def build(instance):
    n = instance["n"]
    costas = cp.intvar(1, n, shape=n, name="costas")
    model = cp.Model(cp.AllDifferent(costas))
    # Row i of the difference triangle holds costas[j] - costas[j - i - 1].
    for i in range(n - 2):
        model += cp.AllDifferent([costas[j] - costas[j - i - 1] for j in range(i + 1, n)])
    return model, {"costas": [costas[i] for i in range(n)]}
