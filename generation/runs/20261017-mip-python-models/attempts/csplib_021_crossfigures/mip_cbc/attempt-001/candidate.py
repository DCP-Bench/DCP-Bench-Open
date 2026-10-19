# CSPLib 021, crossfigures: fill a 9x9 grid so that the numerical clues hold.
# Each white cell holds one digit 0..9; black cells output 0. An answer is the number
# read from the digits of its run (across or down), with no leading zero.
# The instance carries no fields: the grid and the clues are the problem description.
import mip

N = 9
GRID = [
    "1 2 _ 3 X 4 _ 5 6",
    "7 _ X 8 _ _ X 9 _",
    "_ X 10 _ X 11 12 X _",
    "13 14 _ _ X 15 _ 16 _",
    "X _ X X X X X _ X",
    "17 _ 18 19 X 20 21 _ 22",
    "_ X 23 _ X 24 _ X _",
    "25 26 X 27 _ _ X 28 _",
    "29 _ _ _ X 30 _ _ _",
]


def is_prime(p):
    return p > 1 and all(p % q for q in range(2, int(p ** 0.5) + 1))


def build(instance):
    rows = [line.split() for line in GRID]
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # Runs of white cells of length >= 2: ("A", label) across, ("D", label) down.
    runs = {}
    for r in range(N):
        c = 0
        while c < N:
            if rows[r][c] == "X":
                c += 1
                continue
            c0 = c
            while c < N and rows[r][c] != "X":
                c += 1
            if c - c0 >= 2:
                runs[("A", int(rows[r][c0]))] = [(r, k) for k in range(c0, c)]
    for c in range(N):
        r = 0
        while r < N:
            if rows[r][c] == "X":
                r += 1
                continue
            r0 = r
            while r < N and rows[r][c] != "X":
                r += 1
            if r - r0 >= 2:
                runs[("D", int(rows[r0][c]))] = [(k, c) for k in range(r0, r)]

    white = {(r, c) for r in range(N) for c in range(N) if rows[r][c] != "X"}
    d = {}
    for (r, c) in sorted(white):
        d[(r, c)] = model.add_var(f"d_{r}_{c}", var_type=mip.INTEGER, lb=0, ub=9)

    # an answer is a number written in its cells, so its leading digit is not zero
    for key, cells in runs.items():
        model.add_constr(d[cells[0]] >= 1)

    def val(key):
        cells = runs[key]
        L = len(cells)
        return mip.xsum(10 ** (L - 1 - k) * d[cell] for k, cell in enumerate(cells))

    def bounds(key):
        L = len(runs[key])
        return 10 ** (L - 1), 10 ** L - 1

    def times_one_hot(X, lo, hi, zs, cands, name):
        # X * Y where Y = sum cands[i] * zs[i] with exactly one zs[i] = 1
        terms = []
        for i, (c, z) in enumerate(zip(cands, zs)):
            y = model.add_var(f"{name}_{i}", lb=0, ub=hi)
            model.add_constr(y <= hi * z)
            model.add_constr(y >= lo * z)
            model.add_constr(y <= X - lo * (1 - z))
            model.add_constr(y >= X - hi * (1 - z))
            terms.append(c * y)
        return mip.xsum(terms)

    # the value of a run that is a prime / a square, as one-hot choices
    primes2 = [p for p in range(10, 100) if is_prime(p)]
    squares2 = [n * n for n in range(1, 100) if 10 <= n * n < 100]
    squares4 = [n * n for n in range(1, 100) if 1000 <= n * n < 10000]

    # 23 across: a prime number
    z23 = [model.add_var(f"z23_{i}", var_type=mip.BINARY) for i in range(len(primes2))]
    model.add_constr(mip.xsum(z23) == 1)
    model.add_constr(val(("A", 23)) == mip.xsum(c * z for c, z in zip(primes2, z23)))

    # 20 across: a square number
    z20 = [model.add_var(f"z20_{i}", var_type=mip.BINARY) for i in range(len(squares4))]
    model.add_constr(mip.xsum(z20) == 1)
    model.add_constr(val(("A", 20)) == mip.xsum(c * z for c, z in zip(squares4, z20)))

    # 24 across: a square number
    z24 = [model.add_var(f"z24_{i}", var_type=mip.BINARY) for i in range(len(squares2))]
    model.add_constr(mip.xsum(z24) == 1)
    model.add_constr(val(("A", 24)) == mip.xsum(c * z for c, z in zip(squares2, z24)))

    # 13 across: 26 down times 23 across
    lo26, hi26 = bounds(("D", 26))
    model.add_constr(
        val(("A", 13))
        == times_one_hot(val(("D", 26)), lo26, hi26, z23, primes2, "p13")
    )
    # 17 across: 25 across times 23 across
    lo25, hi25 = bounds(("A", 25))
    model.add_constr(
        val(("A", 17))
        == times_one_hot(val(("A", 25)), lo25, hi25, z23, primes2, "p17")
    )

    # 1 across: 27 across times two
    model.add_constr(val(("A", 1)) == 2 * val(("A", 27)))
    # 4 across: 4 down plus seventy-one
    model.add_constr(val(("A", 4)) == val(("D", 4)) + 71)
    # 7 across: 18 down plus four
    model.add_constr(val(("A", 7)) == val(("D", 18)) + 4)
    # 8 across: 6 down divided by sixteen
    model.add_constr(16 * val(("A", 8)) == val(("D", 6)))
    # 9 across: 2 down minus eighteen
    model.add_constr(val(("A", 9)) == val(("D", 2)) - 18)
    # 10 across: Dozen in six gross
    model.add_constr(val(("A", 10)) == 6 * 12 * 12 // 12)
    # 11 across: 5 down minus seventy
    model.add_constr(val(("A", 11)) == val(("D", 5)) - 70)
    # 15 across: 6 down minus 350
    model.add_constr(val(("A", 15)) == val(("D", 6)) - 350)
    # 25 across: 20 across divided by seventeen
    model.add_constr(17 * val(("A", 25)) == val(("A", 20)))
    # 27 across: 6 down divided by four
    model.add_constr(4 * val(("A", 27)) == val(("D", 6)))
    # 28 across: Four dozen
    model.add_constr(val(("A", 28)) == 4 * 12)
    # 29 across: Seven gross
    model.add_constr(val(("A", 29)) == 7 * 12 * 12)
    # 30 across: 22 down plus 450
    model.add_constr(val(("A", 30)) == val(("D", 22)) + 450)

    # 1 down: 1 across plus twenty-seven
    model.add_constr(val(("D", 1)) == val(("A", 1)) + 27)
    # 2 down: Five dozen
    model.add_constr(val(("D", 2)) == 5 * 12)
    # 3 down: 30 across plus 888
    model.add_constr(val(("D", 3)) == val(("A", 30)) + 888)
    # 4 down: Two times 17 across
    model.add_constr(val(("D", 4)) == 2 * val(("A", 17)))
    # 5 down: 29 across divided by twelve
    model.add_constr(12 * val(("D", 5)) == val(("A", 29)))
    # 6 down: 28 across times 23 across
    model.add_constr(val(("D", 6)) == 4 * 12 * val(("A", 23)))
    # 10 down: 10 across plus four
    model.add_constr(val(("D", 10)) == val(("A", 10)) + 4)
    # 12 down: Three times 24 across
    model.add_constr(val(("D", 12)) == 3 * val(("A", 24)))
    # 14 down: 13 across divided by sixteen
    model.add_constr(16 * val(("D", 14)) == val(("A", 13)))
    # 16 down: 28 down times fifteen
    model.add_constr(val(("D", 16)) == 15 * val(("D", 28)))
    # 17 down: 13 across minus 399
    model.add_constr(val(("D", 17)) == val(("A", 13)) - 399)
    # 18 down: 29 across divided by eighteen
    model.add_constr(18 * val(("D", 18)) == val(("A", 29)))
    # 19 down: 22 down minus ninety-four
    model.add_constr(val(("D", 19)) == val(("D", 22)) - 94)
    # 20 down: 20 across minus nine
    model.add_constr(val(("D", 20)) == val(("A", 20)) - 9)
    # 21 down: 25 across minus fifty-two
    model.add_constr(val(("D", 21)) == val(("A", 25)) - 52)
    # 22 down: 20 down times six
    model.add_constr(val(("D", 22)) == 6 * val(("D", 20)))
    # 26 down: Five times 24 across
    model.add_constr(val(("D", 26)) == 5 * val(("A", 24)))
    # 28 down: 21 down plus twenty-seven
    model.add_constr(val(("D", 28)) == val(("D", 21)) + 27)

    out = [[(d[(r, c)] if (r, c) in white else 0) for c in range(N)] for r in range(N)]
    return model, {"M": out}
