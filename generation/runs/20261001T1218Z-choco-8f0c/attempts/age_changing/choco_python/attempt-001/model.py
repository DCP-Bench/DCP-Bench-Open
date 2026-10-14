# Age changing (Enigma 1224): starting from my age and applying +2, /8, -3 and *7 in some order
# gives my husband's age; starting from his age and applying the same four operations in a
# different order gives my age. What are our two ages?
from pychoco.model import Model

# The puzzle has no instance data: the operations, the age range 16..120 and the range 1..1000 of
# intermediate values are the bounds the puzzle statement and its reference fix.
N_OPS = 4  # operation 0 = +2, 1 = /8, 2 = -3, 3 = *7
AGE_LOW, AGE_HIGH = 16, 120
VALUE_LOW, VALUE_HIGH = 1, 1000


def apply(op, old):
    """The value after applying operation op to old, or None when it is not a whole value.
    Division by 8 only applies to multiples of 8."""
    if op == 0:
        return old + 2
    if op == 1:
        return old // 8 if old % 8 == 0 else None
    if op == 2:
        return old - 3
    return old * 7


def build(instance):
    del instance  # the puzzle carries no instance data

    model = Model()

    m = model.intvar(AGE_LOW, AGE_HIGH, name="m")  # my age
    h = model.intvar(AGE_LOW, AGE_HIGH, name="h")  # my husband's age

    # perm1[i] / perm2[i] = the operation applied at step i on the way from my age to his, and
    # from his age to mine
    perm1 = [model.intvar(0, N_OPS - 1, name=f"perm1_{i}") for i in range(N_OPS)]
    perm2 = [model.intvar(0, N_OPS - 1, name=f"perm2_{i}") for i in range(N_OPS)]
    # hlist[i] / mlist[i] = the intermediate values along each chain
    hlist = [model.intvar(VALUE_LOW, VALUE_HIGH, name=f"hlist_{i}") for i in range(N_OPS + 1)]
    mlist = [model.intvar(VALUE_LOW, VALUE_HIGH, name=f"mlist_{i}") for i in range(N_OPS + 1)]

    # Each chain applies all four operations, each once.
    model.all_different(perm1).post()
    model.all_different(perm2).post()

    # The two orders are different: they differ in at least one position.
    differs = [model.arithm(perm1[i], "!=", perm2[i]).reify() for i in range(N_OPS)]
    model.sum(differs, ">=", 1).post()

    # Starting from my age, the operations end at my husband's age, and the other way round.
    model.arithm(hlist[0], "=", m).post()
    model.arithm(hlist[N_OPS], "=", h).post()
    model.arithm(mlist[0], "=", h).post()
    model.arithm(mlist[N_OPS], "=", m).post()

    # Each step applies its operation: (operation, value before, value after) must be a row of
    # this table, which lists every operation on every value whose result stays in range.
    steps = []
    for op in range(N_OPS):
        for old in range(VALUE_LOW, VALUE_HIGH + 1):
            new = apply(op, old)
            if new is not None and VALUE_LOW <= new <= VALUE_HIGH:
                steps.append((op, old, new))
    for i in range(N_OPS):
        model.table([perm1[i], hlist[i], hlist[i + 1]], steps).post()
        model.table([perm2[i], mlist[i], mlist[i + 1]], steps).post()

    return model, {"m": m, "h": h}
