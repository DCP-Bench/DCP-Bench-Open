from ortools.sat.python import cp_model


def build(instance):
    """Curious set of integers: extend {1, 3, 8, 120}, where the product of
    any two members is one less than a perfect square.
    """
    n = instance["n"]
    max_val = instance["max_val"]

    model = cp_model.CpModel()
    x = [model.new_int_var(0, max_val, f"x{i}") for i in range(n)]
    number = x[-1]

    model.add_all_different(x)
    # The four known members of the set are part of the problem statement.
    known = [1, 3, 8, 120]
    for index, value in enumerate(known):
        model.add(x[index] == value)

    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            root = model.new_int_var(0, max_val, f"root_{i}_{j}")
            square = model.new_int_var(0, max_val * max_val, f"sq_{i}_{j}")
            product = model.new_int_var(0, max_val * max_val, f"prod_{i}_{j}")
            model.add_multiplication_equality(square, [root, root])
            model.add_multiplication_equality(product, [x[i], x[j]])
            model.add(square == product + 1)

    return model, {"number": number}
