import z3


def build(instance):
    n = instance["n"]
    costas = [z3.Int(f"costas_{i}") for i in range(n)]
    constraints = [z3.And(mark >= 1, mark <= n) for mark in costas]
    constraints.append(z3.Distinct(costas))
    # Difference triangle: row i holds costas[j] - costas[j - i - 1] for j > i,
    # and every row up to n-3 must have distinct entries. The reference keeps
    # these as auxiliary variables; only costas is a declared output, so they
    # stay plain expressions here.
    for i in range(n - 2):
        row = [costas[j] - costas[j - i - 1] for j in range(i + 1, n)]
        constraints.append(z3.Distinct(row))
    return constraints, {"costas": costas}
