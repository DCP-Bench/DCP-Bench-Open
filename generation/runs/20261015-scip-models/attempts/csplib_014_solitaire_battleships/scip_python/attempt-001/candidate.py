# Solitaire battleships (CSPLib 014): fill the grid so that each cell is water, a submarine, or a
# ship part (left, right, top, bottom, middle). Ships are straight, no two ships touch (not even
# diagonally), the row and column sums give the number of occupied cells, the fleet gives the
# number of ships of each length, and the hint cells are fixed.
from pyscipopt import Model, quicksum

KINDS = ["WATER", "CIRCLE", "LEFT", "RIGHT", "TOP", "BOTTOM", "MIDDLE"]


def build(instance):
    nr, nc = instance["rows"], instance["cols"]
    # grid value of each cell kind, taken from the instance
    code = {k: instance[k] for k in KINDS}
    kind_of = {v: k for k, v in code.items()}
    # fleet_counts lists [ship length, number of ships of that length]
    fleet = {length: count for length, count in instance["fleet_counts"]}
    m = Model("battleships")

    def inside(r, c):
        return 0 <= r < nr and 0 <= c < nc

    # x[r,c,k] = 1 if cell (r,c) has kind k (exactly one kind per cell)
    x = {(r, c, k): m.addVar(name=f"x[{r},{c},{k}]", vtype="B")
         for r in range(nr) for c in range(nc) for k in KINDS}
    # a middle ship cell is either in a horizontal ship (mh) or a vertical one (mv)
    mh = {(r, c): m.addVar(name=f"mh[{r},{c}]", vtype="B") for r in range(nr) for c in range(nc)}
    mv = {(r, c): m.addVar(name=f"mv[{r},{c}]", vtype="B") for r in range(nr) for c in range(nc)}
    # hs[r,c,L] = 1 if a horizontal ship of length L starts at (r,c); vs is the vertical analogue
    hs, vs = {}, {}
    for L in fleet:
        if L < 2:
            continue
        for r in range(nr):
            for c in range(nc):
                if c + L - 1 < nc:
                    hs[r, c, L] = m.addVar(name=f"hs[{r},{c},{L}]", vtype="B")
                if r + L - 1 < nr:
                    vs[r, c, L] = m.addVar(name=f"vs[{r},{c},{L}]", vtype="B")

    def need(lhs, q, kinds):
        # if lhs is 1, the neighbour q must be one of the kinds (off the grid it cannot be)
        cells = [x[q[0], q[1], k] for k in kinds] if inside(*q) else []
        m.addCons(lhs <= quicksum(cells))

    def need_water(lhs, q):
        # if lhs is 1, the neighbour q must be water (off the grid it is water already)
        if inside(*q):
            m.addCons(lhs <= x[q[0], q[1], "WATER"])

    for r in range(nr):
        for c in range(nc):
            up, down, left, right = (r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)
            # one kind per cell
            m.addCons(quicksum(x[r, c, k] for k in KINDS) == 1)
            # a middle cell is one of the two orientations
            m.addCons(x[r, c, "MIDDLE"] == mh[r, c] + mv[r, c])
            # a left end: the cell to its right continues the ship, everything else around it is water
            need(x[r, c, "LEFT"], right, ["RIGHT", "MIDDLE"])
            need_water(x[r, c, "LEFT"], left)
            need_water(x[r, c, "LEFT"], up)
            need_water(x[r, c, "LEFT"], down)
            # a right end: the cell to its left continues the ship, everything else around it is water
            need(x[r, c, "RIGHT"], left, ["LEFT", "MIDDLE"])
            need_water(x[r, c, "RIGHT"], right)
            need_water(x[r, c, "RIGHT"], up)
            need_water(x[r, c, "RIGHT"], down)
            # a top end: the cell below continues the ship
            need(x[r, c, "TOP"], down, ["BOTTOM", "MIDDLE"])
            need_water(x[r, c, "TOP"], up)
            need_water(x[r, c, "TOP"], left)
            need_water(x[r, c, "TOP"], right)
            # a bottom end: the cell above continues the ship
            need(x[r, c, "BOTTOM"], up, ["TOP", "MIDDLE"])
            need_water(x[r, c, "BOTTOM"], down)
            need_water(x[r, c, "BOTTOM"], left)
            need_water(x[r, c, "BOTTOM"], right)
            # a submarine is alone: all four neighbours are water
            for q in (up, down, left, right):
                need_water(x[r, c, "CIRCLE"], q)
            # a horizontal middle cell has ship on both sides and water above and below
            need(mh[r, c], left, ["LEFT", "MIDDLE"])
            need(mh[r, c], right, ["RIGHT", "MIDDLE"])
            need_water(mh[r, c], up)
            need_water(mh[r, c], down)
            # a vertical middle cell has ship above and below and water on both sides
            need(mv[r, c], up, ["TOP", "MIDDLE"])
            need(mv[r, c], down, ["BOTTOM", "MIDDLE"])
            need_water(mv[r, c], left)
            need_water(mv[r, c], right)
            # ships do not touch diagonally: of two diagonal cells, at least one is water
            for dr, dc in ((1, 1), (1, -1)):
                if inside(r + dr, c + dc):
                    m.addCons(x[r, c, "WATER"] + x[r + dr, c + dc, "WATER"] >= 1)

    # each left end starts exactly one horizontal ship, and each top end exactly one vertical ship
    for r in range(nr):
        for c in range(nc):
            m.addCons(x[r, c, "LEFT"] == quicksum(v for (rr, cc, _), v in hs.items() if (rr, cc) == (r, c)))
            m.addCons(x[r, c, "TOP"] == quicksum(v for (rr, cc, _), v in vs.items() if (rr, cc) == (r, c)))

    # a horizontal ship of length L starting at (r,c): its middle cells are horizontal middles, its
    # last cell is a right end
    for (r, c, L), v in hs.items():
        for k in range(1, L - 1):
            m.addCons(mh[r, c + k] >= v)
        m.addCons(x[r, c + L - 1, "RIGHT"] >= v)
    # a vertical ship of length L starting at (r,c): the same, vertically
    for (r, c, L), v in vs.items():
        for k in range(1, L - 1):
            m.addCons(mv[r + k, c] >= v)
        m.addCons(x[r + L - 1, c, "BOTTOM"] >= v)

    # the fleet: the number of submarines (length 1) and of ships of each longer length
    for L, count in fleet.items():
        if L == 1:
            m.addCons(quicksum(x[r, c, "CIRCLE"] for r in range(nr) for c in range(nc)) == count)
        else:
            m.addCons(quicksum(v for (_, _, LL), v in hs.items() if LL == L)
                      + quicksum(v for (_, _, LL), v in vs.items() if LL == L) == count)

    # row and column sums: the number of occupied (non-water) cells in each row and column
    for r in range(nr):
        m.addCons(quicksum(x[r, c, k] for c in range(nc) for k in KINDS if k != "WATER") == instance["rowsum"][r])
    for c in range(nc):
        m.addCons(quicksum(x[r, c, k] for r in range(nr) for k in KINDS if k != "WATER") == instance["colsum"][c])

    # hints: given cells, each as [row, col, kind code]
    for r, c, k in instance["hints"]:
        m.addCons(x[r, c, kind_of[k]] == 1)

    grid = [[quicksum(code[k] * x[r, c, k] for k in KINDS) for c in range(nc)] for r in range(nr)]
    return m, {"grid": grid}
