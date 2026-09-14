from ortools.sat.python import cp_model


def build(instance):
    n, c = instance["n"], instance["c"]
    model = cp_model.CpModel()
    balls = [model.new_int_var(1, c, f"balls_{i}") for i in range(n)]
    for x in range(1, n):
        for y in range(1, n - x + 1):
            z = x + y
            if z > n:
                continue
            # At least one of the three pairs must differ.
            literals = []
            for first, second in ((x, y), (x, z), (y, z)):
                literal = model.new_bool_var(f"differ_{x}_{y}_{first}_{second}")
                model.add(balls[first - 1] != balls[second - 1]).only_enforce_if(literal)
                literals.append(literal)
            model.add_bool_or(literals)
    return model, {"balls": balls}
