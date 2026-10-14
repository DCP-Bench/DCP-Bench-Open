# Five brigands: Alfonso, Benito, Carlos, Diego and Esteban share 200 doubloons,
# each has at least one, and the total would still be 200 if Alfonso had twelve
# times as much, Benito three times, Carlos the same, Diego half and Esteban a third.
from exact import Exact

# 12A + 3B + C + D/2 + E/3 = 200, multiplied by 6 to get whole numbers
TIMES_SIX = {"A": 72, "B": 18, "C": 6, "D": 3, "E": 2}


def build(instance):
    # The puzzle is fixed by the problem; the instance carries no data.
    solver = Exact()
    # a brigand has between 1 and 200 doubloons
    for name in TIMES_SIX:
        solver.addVariable(name, 1, 200)

    # together they have 200 doubloons
    solver.addConstraint([(1, name) for name in TIMES_SIX], True, 200, True, 200)
    # with the changed amounts they would still have 200 (times 6)
    solver.addConstraint([(c, name) for name, c in TIMES_SIX.items()], True, 1200, True, 1200)

    return solver, {name: name for name in TIMES_SIX}
