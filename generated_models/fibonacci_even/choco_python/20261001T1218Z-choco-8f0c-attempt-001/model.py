# Even Fibonacci numbers (Project Euler 2): the sum of the even-valued Fibonacci terms that do not
# exceed four million.
from pychoco.model import Model

# The puzzle has no instance data. The limit of four million is its statement; 35 terms and the
# bound 10^7 on a term are the reference's choices (the 35th term, 9227465, is past the limit).
N_TERMS = 35
LIMIT = 4000000
MAX_TERM = 10000000
MAX_SUM = 100000000


def build(instance):
    del instance  # the puzzle carries no instance data

    model = Model()

    # f[i] = the i-th Fibonacci number, f[0] = 0 and f[1] = f[2] = 1
    f = [model.intvar(0, MAX_TERM, name=f"f_{i}", bounded_domain=True) for i in range(N_TERMS + 1)]
    model.arithm(f[0], "=", 0).post()
    model.arithm(f[1], "=", 1).post()
    model.arithm(f[2], "=", 1).post()
    # Each new term is the sum of the previous two.
    for i in range(3, N_TERMS + 1):
        model.scalar([f[i], f[i - 1], f[i - 2]], [1, -1, -1], "=", 0).post()

    # x[i] is true exactly when term i is even and below four million.
    zero = model.intvar(0, 0, name="zero")
    terms = []
    for i in range(1, N_TERMS + 1):
        # f[i] = 2 * half + odd, so f[i] is even when odd = 0
        half = model.intvar(0, MAX_TERM // 2, name=f"half_{i}", bounded_domain=True)
        odd = model.boolvar(name=f"odd_{i}")
        model.scalar([f[i], half, odd], [1, -2, -1], "=", 0).post()
        small = model.arithm(f[i], "<", LIMIT).reify()
        x = model.boolvar(name=f"x_{i}")
        # x = (not odd) and small
        model.arithm(x, "<=", small).post()
        model.arithm(x, "+", odd, "<=", 1).post()
        model.scalar([x, small, odd], [1, -1, 1], ">=", 0).post()
        # the contribution of term i to the sum: f[i] when x, otherwise 0
        term = model.intvar(0, MAX_TERM, name=f"term_{i}", bounded_domain=True)
        model.element(term, [zero, f[i]], x).post()
        terms.append(term)

    # res is the sum of the selected terms.
    res = model.intvar(0, MAX_SUM, name="res", bounded_domain=True)
    model.sum(terms, "=", res).post()

    return model, {"res": res}
