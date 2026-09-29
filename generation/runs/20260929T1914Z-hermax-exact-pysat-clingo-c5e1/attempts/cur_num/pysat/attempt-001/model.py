# Curious number: 48 has the peculiarity that adding 1 to it gives a square and
# adding 1 to its half gives a square. Find another number, from 1 to 10000, with it.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    # The puzzle is fixed by the problem; the instance carries no data.
    limit = 10000  # the number and every number derived from it is at most 10000
    pool = IDPool()
    # peculiar + 1 is at most 10000
    peculiar = Integer("peculiar", 1, limit - 1, vpool=pool)
    # the square roots of peculiar + 1 and of peculiar / 2 + 1, at most 100 since the squares are at most 10000
    root_of_number = Integer("root_of_number", 1, 100, vpool=pool)
    root_of_half = Integer("root_of_half", 1, 100, vpool=pool)
    engine = IntegerEngine(vars=[peculiar, root_of_number, root_of_half], vpool=pool)
    cnf = engine.clausify()

    # 48 is already known
    cnf.append([-peculiar.equals(48)])

    for root in range(1, 101):
        # peculiar + 1 is the square of root_of_number
        value = root * root - 1
        if 1 <= value <= limit - 1:
            cnf.append([-root_of_number.equals(root), peculiar.equals(value)])
        else:
            cnf.append([-root_of_number.equals(root)])
        # peculiar is twice a number c >= 1 and c + 1 is the square of root_of_half
        value = 2 * (root * root - 1)
        if 1 <= value <= limit - 1:
            cnf.append([-root_of_half.equals(root), peculiar.equals(value)])
        else:
            cnf.append([-root_of_half.equals(root)])

    return cnf, {"peculiar": peculiar}
