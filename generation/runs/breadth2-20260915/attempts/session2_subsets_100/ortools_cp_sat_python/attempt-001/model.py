from ortools.sat.python import cp_model


def build(instance):
    values = instance["A"]
    n = len(values)
    model = cp_model.CpModel()
    in_s = [model.new_bool_var(f"s_{i}") for i in range(n)]
    in_t = [model.new_bool_var(f"t_{i}") for i in range(n)]
    model.add(sum(values[i] * in_s[i] for i in range(n))
              == sum(values[i] * in_t[i] for i in range(n)))
    for i in range(n):
        model.add_at_most_one([in_s[i], in_t[i]])
    model.add(sum(in_s) >= 1)
    model.add(sum(in_t) >= 1)
    return model, {"in_S": in_s, "in_T": in_t}
