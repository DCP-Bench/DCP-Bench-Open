# Rectangle packing: place rectangular items (no rotation) without overlap
# inside an enclosing rectangle whose sides are chosen too, so that the area
# of the enclosing rectangle is as small as possible.
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine


def build(instance):
    widths = instance["widths"]
    heights = instance["heights"]
    n = len(widths)

    # The enclosing rectangle is at least as wide as the widest item and at
    # most as wide as all items side by side; likewise for its height. These
    # are the reference's bounds.
    area_min_x, area_max_x = max(widths), sum(widths)
    area_min_y, area_max_y = max(heights), sum(heights)

    pool = IDPool()
    # Coupled encodings throughout: the order half states "at least so far
    # along" with short clauses, the direct half gives the "== v" literals the
    # runner blocks on and the objective pays on.
    pos_x = [Integer(f"pos_x{i}", 0, area_max_x, encoding="coupled", vpool=pool)
             for i in range(n)]
    pos_y = [Integer(f"pos_y{i}", 0, area_max_y, encoding="coupled", vpool=pool)
             for i in range(n)]
    total_x = Integer("total_x", area_min_x, max(area_max_x, area_min_x + 1),
                      encoding="coupled", vpool=pool)
    total_y = Integer("total_y", area_min_y, max(area_max_y, area_min_y + 1),
                      encoding="coupled", vpool=pool)
    engine = IntegerEngine(vars=pos_x + pos_y + [total_x, total_y], vpool=pool)
    engine.add_linear(total_x <= area_max_x)
    engine.add_linear(total_y <= area_max_y)

    formula = WCNF()
    formula.extend(engine.clausify().clauses)

    def ge(x, v, lb, ub):
        """x >= v as a literal; True when v <= lb, False when v > ub."""
        if v <= lb:
            return True
        if v > ub:
            return False
        return x.ge(v)

    def precedes(cond, a, a_lb, a_ub, size, b, b_lb, b_ub):
        """Clauses for: cond implies a + size <= b (cond None means always)."""
        head = [] if cond is None else [-cond]
        # for every v that a reaches, b reaches v + size
        for v in range(a_lb, a_ub + 1):
            lhs = ge(a, v, a_lb, a_ub)
            if lhs is False:
                continue
            rhs = ge(b, v + size, b_lb, b_ub)
            if rhs is True:
                continue
            clause = list(head)
            if lhs is not True:
                clause.append(-lhs)
            if rhs is not False:
                clause.append(rhs)
            formula.append(clause)

    tx_ub = max(area_max_x, area_min_x + 1)
    ty_ub = max(area_max_y, area_min_y + 1)

    # Every item has to be within the overall area.
    for i in range(n):
        precedes(None, pos_x[i], 0, area_max_x, widths[i], total_x, area_min_x, tx_ub)
        precedes(None, pos_y[i], 0, area_max_y, heights[i], total_y, area_min_y, ty_ub)

    # No overlap: every item is fully left of, right of, below or above every
    # other item. Each case gets a literal that implies it, and one of the
    # four must hold.
    for i in range(n):
        for j in range(i + 1, n):
            left = pool.id(("left", i, j))     # i ends before j starts in x
            right = pool.id(("left", j, i))    # j ends before i starts in x
            below = pool.id(("below", i, j))   # i ends before j starts in y
            above = pool.id(("below", j, i))   # j ends before i starts in y
            formula.append([left, right, below, above])
            precedes(left, pos_x[i], 0, area_max_x, widths[i], pos_x[j], 0, area_max_x)
            precedes(right, pos_x[j], 0, area_max_x, widths[j], pos_x[i], 0, area_max_x)
            precedes(below, pos_y[i], 0, area_max_y, heights[i], pos_y[j], 0, area_max_y)
            precedes(above, pos_y[j], 0, area_max_y, heights[j], pos_y[i], 0, area_max_y)

    # The enclosing rectangle must hold the items' total area, so a pair of
    # sides whose product is smaller is impossible. This follows from the
    # constraints above; stating it saves the solver proving it.
    item_area = sum(w * h for w, h in zip(widths, heights))
    # Minimise the area total_x * total_y: choosing sides W and H pays W * H.
    for W in range(area_min_x, area_max_x + 1):
        for H in range(area_min_y, area_max_y + 1):
            if W * H < item_area:
                formula.append([-total_x.equals(W), -total_y.equals(H)])
            elif W * H > 0:
                formula.append([-total_x.equals(W), -total_y.equals(H)], weight=W * H)

    return formula, {"pos_x": pos_x, "pos_y": pos_y,
                     "total_x": total_x, "total_y": total_y}
