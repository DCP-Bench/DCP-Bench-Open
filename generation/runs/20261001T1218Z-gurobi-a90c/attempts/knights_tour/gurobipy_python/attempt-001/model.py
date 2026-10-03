"""Knight's tour: number the squares of an n-by-n board 0..n*n-1 in the order a knight visits them, every square once, each move a knight's move."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    n = instance["n"]
    N = n * n
    squares = [(i, j) for i in range(n) for j in range(n)]
    knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]

    model = gp.Model("knights_tour")

    # x[i, j] is the move number at which the knight is on square (i, j).
    x = {s: model.addVar(lb=0, ub=N - 1, vtype=GRB.INTEGER, name=f"x[{s[0]},{s[1]}]") for s in squares}

    # move[p, q] is 1 when the knight's next move goes from square p to square
    # q; it exists only for squares a knight's move apart. A one-hot of every
    # move number on every square would need (n*n)**2 binaries, beyond the
    # licence's 2000-variable limit at n = 10.
    move = {}
    for (i, j) in squares:
        for a, b in knight_moves:
            if 0 <= i + a < n and 0 <= j + b < n:
                move[(i, j), (i + a, j + b)] = model.addVar(vtype=GRB.BINARY, name=f"move[{i},{j},{i + a},{j + b}]")

    # When the knight moves from p to q, the number on q is one more than on p.
    for (p, q), m in move.items():
        model.addConstr((m == 1) >> (x[q] == x[p] + 1), name=f"next_number[{p},{q}]")

    # Each square is left at most once and entered at most once, and the tour
    # has n*n - 1 moves. Numbers grow along every move, so the moves hold no
    # loop and form one path over all squares; its n*n numbers are consecutive
    # within 0..n*n-1, so every square is visited exactly once (all numbers
    # differ), and every square but the last has its successor a knight's move
    # away, every square but the first its predecessor.
    for p in squares:
        model.addConstr(gp.quicksum(m for (s, _), m in move.items() if s == p) <= 1, name=f"leave[{p}]")
        model.addConstr(gp.quicksum(m for (_, t), m in move.items() if t == p) <= 1, name=f"enter[{p}]")
    model.addConstr(gp.quicksum(move.values()) == N - 1, name="tour_length")

    return model, {"x": [[x[i, j] for j in range(n)] for i in range(n)]}
