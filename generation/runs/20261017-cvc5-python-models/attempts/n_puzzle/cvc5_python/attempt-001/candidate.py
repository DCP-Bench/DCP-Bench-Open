# N-Puzzle: slide the tiles of a square grid into the end configuration, one
# move per step, printing the grid at every step (start and end included).
# The blank is the tile 0. Grid size n and step count N_STEPS come from the instance.
import cvc5.pythonic as cz


def build(instance):
    start = instance["puzzle_start"]
    end = instance["puzzle_end"]
    steps = instance["N_STEPS"]
    n = len(start)
    top = n * n - 1
    cells = [(r, c) for r in range(n) for c in range(n)]

    # One grid of integer variables per step.
    S = [[[cz.Int(f"s_{t}_{r}_{c}") for c in range(n)] for r in range(n)] for t in range(steps)]

    constraints = []

    # Each state is a permutation of 0..n*n-1 (tiles and the blank).
    # The tile values are bounded by the grid size, so the variables are finite.
    for t in range(steps):
        g = S[t]
        for r, c in cells:
            constraints.append(g[r][c] >= 0)
            constraints.append(g[r][c] <= top)
        constraints.append(cz.Distinct([g[r][c] for r, c in cells]))

    # The first state is the start configuration and the last is the end configuration.
    for r, c in cells:
        constraints.append(S[0][r][c] == start[r][c])
        constraints.append(S[steps - 1][r][c] == end[r][c])

    # Freezing is not allowed: every step is one move of the blank to an adjacent cell,
    # which swaps the blank with the tile it moves over and leaves all other cells as they are.
    adjacent = []
    for r, c in cells:
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            rr, cc = r + dr, c + dc
            if 0 <= rr < n and 0 <= cc < n:
                adjacent.append(((r, c), (rr, cc)))

    for t in range(steps - 1):
        cur = S[t]
        nxt = S[t + 1]
        branches = []
        for p, q in adjacent:
            parts = [
                cur[p[0]][p[1]] == 0,
                nxt[p[0]][p[1]] == cur[q[0]][q[1]],
                nxt[q[0]][q[1]] == 0,
            ]
            parts += [nxt[r][c] == cur[r][c] for r, c in cells if (r, c) != p and (r, c) != q]
            branches.append(cz.And(*parts))
        constraints.append(cz.Or(*branches))

    outputs = {
        "steps": [[[S[t][r][c] for c in range(n)] for r in range(n)] for t in range(steps)],
    }
    return constraints, outputs
