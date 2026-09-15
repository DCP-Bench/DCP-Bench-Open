from ortools.sat.python import cp_model


def build(instance):
    # The reference numbers the residents 0 Agatha, 1 the butler, 2 Charles.
    n = len(instance["names"])
    agatha, butler, charles, victim = 0, 1, 2, 0
    model = cp_model.CpModel()
    killer = model.new_int_var(0, n - 1, "killer")
    hates = [[model.new_bool_var(f"hates_{i}_{j}") for j in range(n)] for i in range(n)]
    richer = [[model.new_bool_var(f"richer_{i}_{j}") for j in range(n)] for i in range(n)]
    # A killer always hates, and is no richer than, his victim.
    model.add_element(killer, [hates[i][victim] for i in range(n)], 1)
    model.add_element(killer, [richer[i][victim] for i in range(n)], 0)
    for i in range(n):
        model.add(richer[i][i] == 0)
        for j in range(i + 1, n):
            model.add(richer[i][j] != richer[j][i])
        # Charles hates nobody that Agatha hates.
        model.add_implication(hates[agatha][i], ~hates[charles][i])
        # The butler hates everyone not richer than Agatha, and everyone Agatha hates.
        model.add_implication(~richer[i][agatha], hates[butler][i])
        model.add_implication(hates[agatha][i], hates[butler][i])
        # Nobody hates everyone.
        model.add(sum(hates[i]) <= 2)
    # Agatha hates everybody except the butler.
    model.add(hates[agatha][agatha] == 1)
    model.add(hates[agatha][charles] == 1)
    model.add(hates[agatha][butler] == 0)
    return model, {"killer": killer}
