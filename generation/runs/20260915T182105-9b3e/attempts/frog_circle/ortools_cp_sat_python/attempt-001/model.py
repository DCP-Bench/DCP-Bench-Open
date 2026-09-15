from ortools.sat.python import cp_model


def build(instance):
    """Frog circle: arrange cards 1..n around a circle so the frog, jumping
    from each card by the number written on it, lands on every card.
    """
    n = instance["n"]

    model = cp_model.CpModel()
    x = [model.new_int_var(1, n, f"x{i}") for i in range(n)]
    pos = [model.new_int_var(0, n - 1, f"pos{i}") for i in range(n)]
    visited = [model.new_int_var(1, n, f"visited{i}") for i in range(n)]

    model.add_all_different(x)
    model.add_all_different(pos)
    model.add_all_different(visited)

    # The frog starts on card 1, at position 0.
    model.add(x[0] == 1)
    model.add(pos[0] == 0)
    model.add(visited[0] == 1)

    # The card arrays are read at a position chosen by a decision variable, so
    # AddElement does the lookup; it takes a span of linear expressions.
    cards = [cp_model.LinearExpr.term(value, 1) for value in x]

    for i in range(1, n):
        here = model.new_int_var(1, n, f"here{i}")
        model.add_element(pos[i - 1], cards, here)
        # Jump clockwise by the number on the card just landed on.
        target = model.new_int_var(0, 2 * n, f"target{i}")
        model.add(target == pos[i - 1] + here)
        model.add_modulo_equality(pos[i], target, n)
        model.add_element(pos[i], cards, visited[i])

    return model, {"x": x}
