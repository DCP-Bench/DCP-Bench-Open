import cpmpy as cp


def build(instance):
    """Five floors: put Baker, Cooper, Fletcher, Miller and Smith on five
    different floors under the stated restrictions.

    The puzzle states its own residents and clues, so `instance` is unused.
    """
    del instance

    baker = cp.intvar(1, 5, name="B")
    cooper = cp.intvar(1, 5, name="C")
    fletcher = cp.intvar(1, 5, name="F")
    miller = cp.intvar(1, 5, name="M")
    smith = cp.intvar(1, 5, name="S")

    model = cp.Model(
        baker != 5,
        cooper != 1,
        (fletcher != 5) & (fletcher != 1),
        miller > cooper,
        # Neither Smith nor Cooper is next door to Fletcher.
        cp.abs(smith - fletcher) != 1,
        cp.abs(fletcher - cooper) != 1,
        cp.AllDifferent([baker, cooper, fletcher, miller, smith]),
    )

    return model, {
        "B": baker, "C": cooper, "F": fletcher, "M": miller, "S": smith,
    }
