"""Handshaking: at Hilary and Jocelyn's party everyone but Hilary shook a different number of hands; how many did Hilary shake?"""
from docplex.mp.model import Model


def build(instance):
    n = 2 + 2 * instance["num_couples"]  # the guests' couples plus Hilary (0) and Jocelyn (1)
    people = range(n)
    # Spouses sit next to each other: 0 and 1, 2 and 3, and so on.
    spouse = [p + 1 if p % 2 == 0 else p - 1 for p in people]

    model = Model("handshaking")

    # shake[i, j], for i < j, is 1 when i and j shook hands; nobody shakes hands
    # with themselves or their spouse, so those pairs have no variable at all.
    pairs = [(i, j) for i in people for j in range(i + 1, n) if j != spouse[i]]
    shake = {pair: model.binary_var(name=f"shake_{pair[0]}_{pair[1]}") for pair in pairs}

    def hands(p):
        return model.sum(shake[i, j] for (i, j) in pairs if p in (i, j))

    # Everyone except Hilary shook a different number of hands. Those are n - 1
    # people with counts in 0..n-2, so every count occurs exactly once.
    others = range(1, n)
    counts = range(n - 1)
    has = model.binary_var_matrix(others, counts, name="has")
    for p in others:
        model.add_constraint(model.sum(has[p, c] for c in counts) == 1, ctname=f"one_count_{p}")
        model.add_constraint(hands(p) == model.sum(c * has[p, c] for c in counts), ctname=f"count_{p}")
    for c in counts:
        model.add_constraint(model.sum(has[p, c] for p in others) == 1, ctname=f"distinct_{c}")

    # hil is the number of hands Hilary shook. It is a variable of its own so that
    # the declared output is this one number, not every handshake behind it.
    hil = model.integer_var(0, n - 2, name="hil")
    model.add_constraint(hil == hands(0), ctname="hilary")

    return model, {"hil": hil}
