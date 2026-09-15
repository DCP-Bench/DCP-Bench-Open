from ortools.sat.python import cp_model


def build(instance):
    """Abbot's puzzle: share 100 bushels among 100 people.

    The problem carries no instance data of its own - every number below is
    part of the puzzle statement, which is why `instance` is unused.
    """
    del instance

    model = cp_model.CpModel()
    men = model.new_int_var(0, 100, "men")
    women = model.new_int_var(0, 100, "women")
    children = model.new_int_var(0, 100, "children")

    # One hundred people in total.
    model.add(men + women + children == 100)
    # Three bushels a man, two a woman, half a bushel a child, doubled through
    # so the half stays an integer: 200 half-bushels in all.
    model.add(men * 6 + women * 4 + children == 200)
    # Five times as many women as men.
    model.add(men * 5 == women)

    return model, {"men": men, "women": women, "children": children}
