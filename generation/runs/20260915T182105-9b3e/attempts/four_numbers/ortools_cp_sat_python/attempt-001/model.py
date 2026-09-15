from ortools.sat.python import cp_model


def build(instance):
    """Four numbers: find three values whose subsets sum to every given number.
    """
    numbers = instance["numbers"]
    m = len(numbers)
    n = 3

    model = cp_model.CpModel()
    x = [model.new_int_var(1, 10, f"x{j}") for j in range(n)]

    for i in range(m):
        parts = []
        for j in range(n):
            # tmp says whether x[j] is part of the subset that makes
            # numbers[i]; the product of the two needs its own variable.
            chosen = model.new_bool_var(f"tmp{i}_{j}")
            part = model.new_int_var(0, 10, f"part{i}_{j}")
            model.add(part == x[j]).only_enforce_if(chosen)
            model.add(part == 0).only_enforce_if(~chosen)
            parts.append(part)
        model.add(sum(parts) == numbers[i])

    return model, {"x": x}
