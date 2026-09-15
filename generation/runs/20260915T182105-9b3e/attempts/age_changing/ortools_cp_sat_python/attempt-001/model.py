from ortools.sat.python import cp_model


def build(instance):
    """Age changing: the same four operations, applied in two different orders,
    turn each spouse's age into the other's.

    The puzzle states its own operations and age range, so `instance` is
    unused.  The four operations are +2, /8, -3 and *7, numbered in that order.
    """
    del instance

    n = 4
    age_low, age_high = 16, 120

    model = cp_model.CpModel()
    m = model.new_int_var(age_low, age_high, "m")
    h = model.new_int_var(age_low, age_high, "h")

    perm1 = [model.new_int_var(0, n - 1, f"perm1_{i}") for i in range(n)]
    perm2 = [model.new_int_var(0, n - 1, f"perm2_{i}") for i in range(n)]
    model.add_all_different(perm1)
    model.add_all_different(perm2)

    # Running values as each operation is applied in turn.
    mlist = [model.new_int_var(1, 1000, f"mlist{i}") for i in range(n + 1)]
    hlist = [model.new_int_var(1, 1000, f"hlist{i}") for i in range(n + 1)]

    def check(op, old, new):
        # One indicator per operation, pinned in both directions, so the
        # implication cannot be satisfied by leaving the indicator free.
        # Division is stated as a multiplication so only exact eighths count.
        results = [old + 2, None, old - 3, old * 7]
        for code in range(n):
            chosen = model.new_bool_var("")
            model.add(op == code).only_enforce_if(chosen)
            model.add(op != code).only_enforce_if(~chosen)
            if code == 1:
                model.add(8 * new == old).only_enforce_if(chosen)
            else:
                model.add(new == results[code]).only_enforce_if(chosen)

    # The same operations, but in a different order.
    differs = []
    for i in range(n):
        bit = model.new_bool_var("")
        model.add(perm1[i] != perm2[i]).only_enforce_if(bit)
        model.add(perm1[i] == perm2[i]).only_enforce_if(~bit)
        differs.append(bit)
    model.add(sum(differs) > 0)

    # Start from my age and finish at my husband's, and the other way round.
    model.add(hlist[0] == m)
    model.add(h == hlist[n])
    model.add(mlist[0] == h)
    model.add(m == mlist[n])

    for i in range(n):
        check(perm1[i], hlist[i], hlist[i + 1])
        check(perm2[i], mlist[i], mlist[i + 1])

    return model, {"m": m, "h": h}
