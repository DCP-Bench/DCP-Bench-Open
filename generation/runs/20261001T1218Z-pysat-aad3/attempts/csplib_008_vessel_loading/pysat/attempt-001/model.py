# Vessel loading: place rectangular containers on a rectangular deck, each parallel to
# the deck sides (it may be turned by 90 degrees), without overlapping, so that two
# containers whose classes have a separation distance are at least that far apart.
from itertools import combinations

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def at_least(var, value):
    """Literal for var >= value; True or False when that holds for the whole domain or none of it."""
    if value <= var.lb:
        return True
    if value > var.ub:
        return False
    return var.ge(value)


def negate(lit):
    return (not lit) if isinstance(lit, bool) else -lit


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
    deck_width = instance["deck_width"]    # the horizontal coordinates run 0..deck_width
    deck_length = instance["deck_length"]  # the vertical coordinates run 0..deck_length
    n = instance["n_containers"]
    width = instance["width"]
    length = instance["length"]
    classes = instance["classes"]          # class of each container, numbered from 1
    separation = instance["separation"]    # separation[c1 - 1][c2 - 1] = minimum distance between classes

    pool = IDPool()
    # left/right and bottom/top are the edges of each container, ranging over the deck as in the
    # reference. The coupled encoding gives "v = value" literals (to read the value and to tie the
    # two edges together) and "v >= value" literals (to compare positions without a clause per pair).
    left = [Integer(f"left{i}", 0, deck_width, encoding="coupled", vpool=pool) for i in range(n)]
    right = [Integer(f"right{i}", 0, deck_width, encoding="coupled", vpool=pool) for i in range(n)]
    top = [Integer(f"top{i}", 0, deck_length, encoding="coupled", vpool=pool) for i in range(n)]
    bottom = [Integer(f"bottom{i}", 0, deck_length, encoding="coupled", vpool=pool) for i in range(n)]
    engine = IntegerEngine(vars=left + right + top + bottom, vpool=pool)
    cnf = engine.clausify()

    # turned[i] is true when container i is laid with its length along the deck width
    turned = [pool.id(("turned", i)) for i in range(n)]

    def tie(low, high, size_if_upright, size_if_turned, i):
        """high = low + the container's extent: size_if_upright, or size_if_turned when it is turned."""
        for value in range(low.lb, low.ub + 1):
            for is_turned in (False, True):
                size = size_if_turned if is_turned else size_if_upright
                guard = [-turned[i]] if is_turned else [turned[i]]
                target = value + size
                if target <= high.ub:
                    cnf.append(guard + [-low.equals(value), high.equals(target)])
                else:
                    cnf.append(guard + [-low.equals(value)])

    # each container keeps its shape: right - left and top - bottom are its width and length,
    # or its length and width when it is turned
    for i in range(n):
        tie(left[i], right[i], width[i], length[i], i)
        tie(bottom[i], top[i], length[i], width[i], i)

    def before(key, first_edge, second_edge, gap):
        """A literal that, when true, forces first_edge + gap <= second_edge: for every value t,
        'first_edge >= t' implies 'second_edge >= t + gap'."""
        selector = pool.id(key)
        for t in range(first_edge.lb, first_edge.ub + 1):
            add_clause(cnf, -selector, negate(at_least(first_edge, t)), at_least(second_edge, t + gap))
        return selector

    # no two containers overlap, and they keep the separation of their classes: one is at least
    # that far left of, right of, below or above the other
    for x, y in combinations(range(n), 2):
        sep = separation[classes[x] - 1][classes[y] - 1]
        cnf.append([before(("x_left_of_y", x, y), right[x], left[y], sep),
                    before(("x_right_of_y", x, y), right[y], left[x], sep),
                    before(("x_under_y", x, y), top[x], bottom[y], sep),
                    before(("x_above_y", x, y), top[y], bottom[x], sep)])

    return cnf, {"left": left, "right": right, "top": top, "bottom": bottom}
