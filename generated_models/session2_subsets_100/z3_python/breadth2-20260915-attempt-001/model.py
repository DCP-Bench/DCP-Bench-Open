import z3


def build(instance):
    values = instance["A"]
    n = len(values)
    in_s = [z3.Bool(f"s_{i}") for i in range(n)]
    in_t = [z3.Bool(f"t_{i}") for i in range(n)]
    picked_s = [z3.If(in_s[i], 1, 0) for i in range(n)]
    picked_t = [z3.If(in_t[i], 1, 0) for i in range(n)]
    constraints = [z3.Sum([values[i] * picked_s[i] for i in range(n)])
                   == z3.Sum([values[i] * picked_t[i] for i in range(n)])]
    constraints += [z3.Not(z3.And(in_s[i], in_t[i])) for i in range(n)]
    constraints.append(z3.Sum(picked_s) >= 1)
    constraints.append(z3.Sum(picked_t) >= 1)
    return constraints, {"in_S": in_s, "in_T": in_t}
