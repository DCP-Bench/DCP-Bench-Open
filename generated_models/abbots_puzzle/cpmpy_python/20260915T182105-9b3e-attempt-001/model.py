import cpmpy as cp


def build(instance):
    """Abbot's puzzle: share 100 bushels among 100 people.

    The problem carries no instance data of its own - every number below is
    part of the puzzle statement, which is why `instance` is unused.
    """
    del instance

    men = cp.intvar(0, 100, name="men")
    women = cp.intvar(0, 100, name="women")
    children = cp.intvar(0, 100, name="children")

    model = cp.Model(
        # One hundred people in total.
        men + women + children == 100,
        # Three bushels a man, two a woman, half a bushel a child, doubled
        # through so the half stays an integer: 200 half-bushels in all.
        men * 6 + women * 4 + children == 200,
        # Five times as many women as men.
        men * 5 == women,
    )

    return model, {"men": men, "women": women, "children": children}
