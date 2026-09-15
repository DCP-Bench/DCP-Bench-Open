import cpmpy as cp


def build(instance):
    values = instance["A"]
    n = len(values)
    in_s = cp.boolvar(shape=n, name="in_S")
    in_t = cp.boolvar(shape=n, name="in_T")
    model = cp.Model(cp.sum([values[i] * in_s[i] for i in range(n)])
                     == cp.sum([values[i] * in_t[i] for i in range(n)]))
    # No element lies in both subsets.
    model += [in_s[i] + in_t[i] <= 1 for i in range(n)]
    model += cp.sum([in_s[i] for i in range(n)]) > 0
    model += cp.sum([in_t[i] for i in range(n)]) > 0
    return model, {"in_S": [in_s[i] for i in range(n)], "in_T": [in_t[i] for i in range(n)]}
