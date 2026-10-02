# Exodus: five children (Bernice, Carl, Debby, Sammy, Ted) each tell a different part of the Exodus
# story, have a different age and come from a family from a different country. Clues link them;
# the model returns, for every age, child, country and story, a label 1..5 so that items with the
# same label belong to the same child.
from exact import Exact


def build(instance):
    # This problem has no instance data. The categories, their items and the ages belong to the
    # problem statement.
    n = 5
    age_of = {"age3": 3, "age5": 5, "age7": 7, "age8": 8, "age10": 10}
    kinds = {
        "ages": list(age_of),
        "children": ["bernice", "carl", "debby", "sammy", "ted"],
        "countries": ["ethiopia", "kazakhstan", "lithuania", "morocco", "yemen"],
        "stories": ["burning_bush", "captivity", "moses_youth", "passover", "ten_commandments"],
    }

    solver = Exact()

    # Every item holds a label 1..5. Comparing labels needs 0/1 indicators:
    # is_label[item][p-1] = 1 when the item has label p.
    is_label = {}
    for items in kinds.values():
        for item in items:
            solver.addVariable(item, 1, n)
            is_label[item] = [f"{item}_is_{p}" for p in range(1, n + 1)]
            for indicator in is_label[item]:
                solver.addVariable(indicator, 0, 1)
            solver.addConstraint([(1, indicator) for indicator in is_label[item]], True, 1, True, 1)
            solver.addConstraint([(p, is_label[item][p - 1]) for p in range(1, n + 1)] +
                                 [(-1, item)], True, 0, True, 0)
        # All entities are different per category: every label is used exactly once.
        for p in range(n):
            solver.addConstraint([(1, is_label[item][p]) for item in items], True, 1, True, 1)

    # same_child[(x, y)] = 1 exactly when items x and y have the same label. Two linear
    # inequalities per label channel it: both having label p forces it up, and exactly one of the
    # two having label p forces it down.
    same_child = {}

    def same(x, y):
        if (x, y) not in same_child:
            name = f"same_{x}_{y}"
            solver.addVariable(name, 0, 1)
            for p in range(n):
                solver.addConstraint([(1, name), (-1, is_label[x][p]), (-1, is_label[y][p])],
                                     True, -1)
                solver.addConstraint([(1, name), (1, is_label[x][p]), (-1, is_label[y][p])],
                                     False, 0, True, 1)
            same_child[(x, y)] = name
        return same_child[(x, y)]

    def clue(first, second, holds):
        # "the child of age a1 is `first` and the child of age a2 is `second`" must imply
        # holds(age1, age2). The pairs of ages for which that fails may not both be true.
        for a1, v1 in age_of.items():
            for a2, v2 in age_of.items():
                if not holds(v1, v2):
                    solver.addConstraint([(1, same(a1, first)), (1, same(a2, second))],
                                         False, 0, True, 1)

    # Debby's family is from Lithuania.
    solver.addConstraint([(1, "debby"), (-1, "lithuania")], True, 0, True, 0)
    # The child who told the story of the Passover is two years older than Bernice.
    clue("passover", "bernice", lambda older, younger: older == younger + 2)
    # The child whose family is from Yemen is younger than the child from the Ethiopian family.
    clue("yemen", "ethiopia", lambda younger, older: younger < older)
    # The child from the Moroccan family is three years older than Ted.
    clue("morocco", "ted", lambda older, younger: older == younger + 3)
    # Sammy is three years older than the child who told the story of Moses's youth.
    clue("sammy", "moses_youth", lambda older, younger: older == younger + 3)

    return solver, {kind: items for kind, items in kinds.items()}
