import z3


def build(instance):
    """Abbot's puzzle: share 100 bushels among 100 people.

    The problem carries no instance data of its own, so every number below is
    part of the puzzle statement.
    """
    del instance

    men, women, children = z3.Ints("men women children")
    solver = z3.Solver()
    # Z3 integers are unbounded, so the domains have to be stated.
    solver.add(men >= 0, men <= 100, women >= 0, women <= 100,
               children >= 0, children <= 100)
    # One hundred people in total.
    solver.add(men + women + children == 100)
    # Three bushels a man, two a woman, half a bushel a child, doubled through
    # so the half stays an integer.
    solver.add(men * 6 + women * 4 + children == 200)
    # Five times as many women as men.
    solver.add(men * 5 == women)

    return solver, {"men": men, "women": women, "children": children}
