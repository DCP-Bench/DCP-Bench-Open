from ortools.sat.python import cp_model


def build(instance):
    """Broken weights: split a weight of m pounds into n whole pieces that can
    weigh every integer load from 1 to m on a balance scale.
    """
    m = instance["m"]
    n = instance["n"]

    model = cp_model.CpModel()
    weights = [model.new_int_var(1, m, f"w{j}") for j in range(n)]
    model.add_all_different(weights)
    model.add(sum(weights) == m)

    # x[i][j] is -1, 0 or 1: which pan piece j goes in when weighing load
    # i + 1, or neither. Both pans are allowed, which is what makes a balance
    # scale able to weigh more loads than a simple subset sum.
    for i in range(m):
        placed = []
        for j in range(n):
            side = model.new_int_var(-1, 1, f"x{i}_{j}")
            # weights[j] * side is a product of two variables, so it needs its
            # own bounded variable.
            contribution = model.new_int_var(-m, m, f"c{i}_{j}")
            model.add_multiplication_equality(contribution, [weights[j], side])
            placed.append(contribution)
        model.add(sum(placed) == i + 1)

    return model, {"weights": weights}
