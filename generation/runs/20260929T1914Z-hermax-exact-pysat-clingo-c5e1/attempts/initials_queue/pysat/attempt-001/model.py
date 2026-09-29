# Initials queue: the ten people in a queue have as initials the ten different
# alphabetically ordered pairs of distinct letters from A-E, no one shares a
# letter with the person in front, BE is first, CD second and BD last.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    n = 10  # people in the queue
    letters = 5  # the initials are from A..E, coded 0..4

    pool = IDPool()
    # queue[i][k] = the k-th letter of the i-th person, counted from the front
    queue = [[Integer(f"queue_{i}_{k}", 0, letters - 1, vpool=pool) for k in range(2)] for i in range(n)]
    engine = IntegerEngine(vars=[v for row in queue for v in row], vpool=pool)
    cnf = engine.clausify()

    # the letters of a person are alphabetically ordered and different
    for i in range(n):
        for a in range(letters):
            for b in range(a + 1):
                cnf.append([-queue[i][0].equals(a), -queue[i][1].equals(b)])

    # nobody has the same initials as anybody else
    for i in range(n):
        for j in range(i + 1, n):
            for a in range(letters):
                for b in range(letters):
                    cnf.append([-queue[i][0].equals(a), -queue[i][1].equals(b),
                                -queue[j][0].equals(a), -queue[j][1].equals(b)])

    # nobody shares a letter with the person in front
    for i in range(n - 1):
        for k in range(2):
            for l in range(2):
                for a in range(letters):
                    cnf.append([-queue[i][k].equals(a), -queue[i + 1][l].equals(a)])

    # BE is at the front, CD right behind, BD at the end
    for i, (first, second) in ((0, (1, 4)), (1, (2, 3)), (n - 1, (1, 3))):
        cnf.append([queue[i][0].equals(first)])
        cnf.append([queue[i][1].equals(second)])

    return cnf, {"queue": queue}
