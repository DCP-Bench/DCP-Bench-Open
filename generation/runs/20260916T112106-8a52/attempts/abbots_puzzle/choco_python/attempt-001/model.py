from pychoco.model import Model


def build(instance):
    """Abbot's puzzle: share 100 bushels among 100 people.

    The problem carries no instance data of its own, so every number below is
    part of the puzzle statement.
    """
    del instance

    model = Model()
    men = model.intvar(0, 100, name="men")
    women = model.intvar(0, 100, name="women")
    children = model.intvar(0, 100, name="children")

    # One hundred people in total.
    model.scalar([men, women, children], [1, 1, 1], "=", 100).post()
    # Three bushels a man, two a woman, half a bushel a child, doubled through
    # so the half stays an integer.
    model.scalar([men, women, children], [6, 4, 1], "=", 200).post()
    # Five times as many women as men.
    model.scalar([men, women], [5, -1], "=", 0).post()

    return model, {"men": men, "women": women, "children": children}
