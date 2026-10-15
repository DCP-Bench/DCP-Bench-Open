from pyscipopt import Model, quicksum

# N-Puzzle: find a sequence of N_STEPS states from the start to the end configuration,
# where each step slides one tile into the empty cell (the blank, tile 0).
# The grid size n is taken from the end configuration, so the model covers any n x n puzzle.
def build(instance):
    start = instance["puzzle_start"]
    end = instance["puzzle_end"]
    T = instance["N_STEPS"]
    n = len(end)
    K = n * n  # tile values 0..K-1, with 0 the blank
    cells = [(r, c) for r in range(n) for c in range(n)]
    nbrs = {(r, c): [(r + dr, c + dc)
                     for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1))
                     if 0 <= r + dr < n and 0 <= c + dc < n]
            for (r, c) in cells}

    m = Model()

    # s[t, r, c, k] = 1 if cell (r, c) holds tile k in state t (one-hot over k)
    s = {(t, r, c, k): m.addVar(name=f"s_{t}_{r}_{c}_{k}", vtype="B")
         for t in range(T) for (r, c) in cells for k in range(K)}
    # mv[t, a, b] = 1 if the blank moves from cell a to the adjacent cell b in step t
    mv = {(t, a, b): m.addVar(name=f"mv_{t}_{a[0]}_{a[1]}_{b[0]}_{b[1]}", vtype="B")
          for t in range(T - 1) for a in cells for b in nbrs[a]}

    # each cell holds exactly one tile, and each tile sits in exactly one cell
    for t in range(T):
        # one tile per cell
        for (r, c) in cells:
            m.addCons(quicksum(s[t, r, c, k] for k in range(K)) == 1,
                      name=f"one_tile_{t}_{r}_{c}")
        # one cell per tile
        for k in range(K):
            m.addCons(quicksum(s[t, r, c, k] for (r, c) in cells) == 1,
                      name=f"one_cell_{t}_{k}")

    # the first and last states are the given start and end configurations
    for (r, c) in cells:
        m.addCons(s[0, r, c, start[r][c]] == 1, name=f"start_{r}_{c}")
        m.addCons(s[T - 1, r, c, end[r][c]] == 1, name=f"end_{r}_{c}")

    for t in range(T - 1):
        # exactly one move per step, so every step changes the state ("no freezing")
        m.addCons(quicksum(mv[t, a, b] for a in cells for b in nbrs[a]) == 1,
                  name=f"one_move_{t}")
        # a move leaves from the cell that holds the blank
        for a in cells:
            m.addCons(quicksum(mv[t, a, b] for b in nbrs[a]) <= s[t, a[0], a[1], 0],
                      name=f"move_from_blank_{t}_{a[0]}_{a[1]}")
        # the blank slides into b, so b holds the blank next and a takes the tile from b
        # (a move forces s[t+1, a] = s[t, b] through two linear constraints per tile)
        for a in cells:
            for b in nbrs[a]:
                m.addCons(s[t + 1, b[0], b[1], 0] >= mv[t, a, b],
                          name=f"blank_enters_{t}_{b[0]}_{b[1]}")
                for k in range(K):
                    m.addCons(s[t + 1, a[0], a[1], k] - s[t, b[0], b[1], k]
                              <= 1 - mv[t, a, b],
                              name=f"swap_up_{t}_{a[0]}_{a[1]}_{k}")
                    m.addCons(s[t + 1, a[0], a[1], k] - s[t, b[0], b[1], k]
                              >= mv[t, a, b] - 1,
                              name=f"swap_lo_{t}_{a[0]}_{a[1]}_{k}")
        # cells not touched by the move keep their tile
        for a in cells:
            touched = (quicksum(mv[t, a, b] for b in nbrs[a])
                       + quicksum(mv[t, b, a] for b in nbrs[a]))
            for k in range(K):
                m.addCons(s[t + 1, a[0], a[1], k] - s[t, a[0], a[1], k] <= touched,
                          name=f"keep_up_{t}_{a[0]}_{a[1]}_{k}")
                m.addCons(s[t + 1, a[0], a[1], k] - s[t, a[0], a[1], k] >= -touched,
                          name=f"keep_lo_{t}_{a[0]}_{a[1]}_{k}")

    # steps[t][r][c] = tile value at cell (r, c) in state t
    steps = [[[quicksum(k * s[t, r, c, k] for k in range(K)) for c in range(n)]
              for r in range(n)]
             for t in range(T)]
    return m, {"steps": steps}
