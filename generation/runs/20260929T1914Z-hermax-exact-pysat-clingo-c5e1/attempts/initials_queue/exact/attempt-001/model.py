# Initials queue: the ten people in a queue have as initials the ten different
# alphabetically ordered pairs of distinct letters from A-E, no one shares a
# letter with the person in front, BE is first, CD second and BD last.
from itertools import combinations

from exact import Exact


def build(instance):
    n = 10  # people in the queue
    letters = 5  # the initials are from A..E, coded 0..4
    # the ten possible initials, in alphabetical order
    pairs = list(combinations(range(letters), 2))
    number = {pair: idx for idx, pair in enumerate(pairs)}

    solver = Exact()
    # has[i][p] = 1 when the i-th person, counted from the front, has the initials pairs[p]
    has = [[f"has_{i}_{p}" for p in range(len(pairs))] for i in range(n)]
    for i in range(n):
        for name in has[i]:
            solver.addVariable(name, 0, 1)
        # everybody has exactly one pair of initials
        solver.addConstraint([(1, name) for name in has[i]], True, 1, True, 1)
    # nobody has the same initials as anybody else
    for p in range(len(pairs)):
        solver.addConstraint([(1, has[i][p]) for i in range(n)], False, 0, True, 1)

    # nobody shares a letter with the person in front
    for i in range(n - 1):
        for p, first in enumerate(pairs):
            for q, second in enumerate(pairs):
                if set(first) & set(second):
                    solver.addConstraint([(1, has[i][p]), (1, has[i + 1][q])], False, 0, True, 1)

    # BE is at the front, CD right behind, BD at the end
    for i, pair in ((0, (1, 4)), (1, (2, 3)), (n - 1, (1, 3))):
        solver.addConstraint([(1, has[i][number[pair]])], True, 1, True, 1)

    # queue[i][k] = the k-th letter of the i-th person
    queue = [[f"queue_{i}_{k}" for k in range(2)] for i in range(n)]
    for i in range(n):
        for k in range(2):
            solver.addVariable(queue[i][k], 0, letters - 1)
            terms = [(pair[k], has[i][p]) for p, pair in enumerate(pairs) if pair[k] != 0]
            solver.addConstraint(terms + [(-1, queue[i][k])], True, 0, True, 0)

    return solver, {"queue": queue}
