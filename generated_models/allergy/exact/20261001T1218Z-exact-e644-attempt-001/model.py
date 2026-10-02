# Allergy: four friends (Debra, Janet, Hugh, Rick) each have a different allergy (eggs, mold, nuts,
# ragweed) and a different surname (Baxter, Lemon, Malone, Fleet). Match them using the clues.
from exact import Exact


def build(instance):
    # This problem has no instance data. The four friends are numbered as in the problem.
    n = 4
    debra, janet, hugh, rick = range(n)

    solver = Exact()

    # foods[i] = the friend allergic to food i (eggs, mold, nuts, ragweed);
    # surnames[i] = the friend with surname i (baxter, lemon, malone, fleet).
    foods = ["eggs", "mold", "nuts", "ragweed"]
    surnames = ["baxter", "lemon", "malone", "fleet"]

    # is_friend[name][f] = 1 when variable `name` equals friend f
    is_friend = {}
    for group in (foods, surnames):
        for name in group:
            solver.addVariable(name, 0, n - 1)
            is_friend[name] = [f"{name}_is_{f}" for f in range(n)]
            for indicator in is_friend[name]:
                solver.addVariable(indicator, 0, 1)
            # the variable takes exactly one friend as its value
            solver.addConstraint([(1, x) for x in is_friend[name]], True, 1, True, 1)
            solver.addConstraint([(f, is_friend[name][f]) for f in range(1, n)] + [(-1, name)],
                                 True, 0, True, 0)
        # all different: every friend appears exactly once in the group
        for f in range(n):
            solver.addConstraint([(1, is_friend[name][f]) for name in group], True, 1, True, 1)

    def differs(name, friend):
        solver.addConstraint([(1, is_friend[name][friend])], False, 0, True, 0)

    # Rick is not allergic to mold
    differs("mold", rick)
    # Baxter is allergic to eggs
    solver.addConstraint([(1, "eggs"), (-1, "baxter")], True, 0, True, 0)
    # Hugh is neither surnamed Lemon nor Fleet
    differs("lemon", hugh)
    differs("fleet", hugh)
    # Debra is allergic to ragweed
    solver.addConstraint([(1, "ragweed")], True, debra, True, debra)
    # Janet (who isn't Lemon) is neither allergic to eggs nor to mold
    differs("lemon", janet)
    differs("eggs", janet)
    differs("mold", janet)

    return solver, {name: name for name in foods + surnames}
