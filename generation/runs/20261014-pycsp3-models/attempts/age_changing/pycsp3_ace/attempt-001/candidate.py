from pycsp3 import *

# The problem: my age m and my husband's age h. Four operations are applied in
# some order: 0 is +2, 1 is /8, 2 is -3, 3 is *7. Each order uses every operation once.

# operation used at step k when going from my age to his age
ops_a = VarArray(size=4, dom=range(4))
# operation used at step k when going from his age to my age
ops_b = VarArray(size=4, dom=range(4))

m = Var(dom=range(0, 150))
h = Var(dom=range(0, 150))

# chain of intermediate values from my age to his age
va = VarArray(size=5, dom=range(0, 2000))
# chain of intermediate values from his age to my age
vb = VarArray(size=5, dom=range(0, 2000))


def step(op, v, w):
    # one operation takes the value v to the value w
    return [
        imply(op == 0, w == v + 2),
        imply(op == 1, v == 8 * w),
        imply(op == 2, w == v - 3),
        imply(op == 3, w == 7 * v),
    ]


satisfy(
    # each order uses each of the four operations exactly once
    AllDifferent(ops_a),
    AllDifferent(ops_b),

    # starting from my age, the operations give his age
    va[0] == m,
    va[4] == h,
    [step(ops_a[k], va[k], va[k + 1]) for k in range(4)],

    # starting from his age, the operations give my age
    vb[0] == h,
    vb[4] == m,
    [step(ops_b[k], vb[k], vb[k + 1]) for k in range(4)],

    # the two orders are different
    Or(*[ops_a[k] != ops_b[k] for k in range(4)]),
)
