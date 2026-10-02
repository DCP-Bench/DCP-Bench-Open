# Perfect square placement: pack squares of the given integer sizes into a big square
# without overlap and with all borders parallel to the big square. The areas add up
# to the area of the big square, so the packing leaves no gap.
from itertools import combinations

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine
from pysat.pb import PBEnc


def at_least(var, value):
    """Literal for var >= value; True or False when that holds for the whole domain or none of it."""
    if value <= var.lb:
        return True
    if value > var.ub:
        return False
    return var.ge(value)


def negate(lit):
    return (not lit) if isinstance(lit, bool) else -lit


def at_most(var, value):
    return negate(at_least(var, value + 1))


def add_clause(cnf, *lits):
    """Add the disjunction of lits, which may contain the constants True and False."""
    kept = []
    for lit in lits:
        if lit is True:
            return
        if lit is not False:
            kept.append(lit)
    cnf.append(kept)


def build(instance):
    base = instance["base"]    # side length of the large square
    sides = instance["sides"]  # side lengths of the small squares
    n = len(sides)

    pool = IDPool()
    # x[i], y[i] = coordinates (from 0) of the lower-left corner of square i. A square
    # must lie inside the large square, so its corner is at most base - side.
    # The coupled encoding gives both "x = v" literals (needed to report the value) and
    # "x >= v" literals (needed to compare positions without one clause per value pair).
    x = [Integer(f"x{i}", 0, base - sides[i], encoding="coupled", vpool=pool) for i in range(n)]
    y = [Integer(f"y{i}", 0, base - sides[i], encoding="coupled", vpool=pool) for i in range(n)]
    engine = IntegerEngine(vars=x + y, vpool=pool)
    cnf = engine.clausify()

    def before(key, a, b, size_a):
        """A literal that, when true, forces a + size_a <= b: for every value t of a,
        'a >= t' implies 'b >= t + size_a'."""
        selector = pool.id(key)
        for t in range(a.lb, a.ub + 1):
            add_clause(cnf, -selector, negate(at_least(a, t)), at_least(b, t + size_a))
        return selector

    # no two squares overlap: one lies completely to the left of, or below, the other
    for a, b in combinations(range(n), 2):
        cnf.append([before(("left", a, b), x[a], x[b], sides[a]),
                    before(("left", b, a), x[b], x[a], sides[b]),
                    before(("below", a, b), y[a], y[b], sides[a]),
                    before(("below", b, a), y[b], y[a], sides[b])])

    # Redundant constraint. The areas add up to the area of the big square, so the
    # squares tile it with no gap: every unit-wide column (and every unit-high row)
    # of the big square is crossed by squares whose sides add up to base. It follows
    # from the constraints above and is added because it prunes the search a lot.
    for axis, position in (("column", x), ("row", y)):
        for c in range(base):
            lits, weights, fixed = [], [], 0
            for i in range(n):
                # square i crosses the line c exactly when c - side < position <= c
                low = at_least(position[i], c - sides[i] + 1)
                high = at_most(position[i], c)
                if low is True and high is True:
                    fixed += sides[i]
                    continue
                if low is False or high is False:
                    continue
                crosses = pool.id((axis, c, i))
                add_clause(cnf, -crosses, low)
                add_clause(cnf, -crosses, high)
                add_clause(cnf, crosses, negate(low), negate(high))
                lits.append(crosses)
                weights.append(sides[i])
            if lits:
                cnf.extend(PBEnc.equals(lits=lits, weights=weights, bound=base - fixed,
                                        vpool=pool).clauses)

    return cnf, {"x_coords": x, "y_coords": y}
