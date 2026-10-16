from pycsp3 import *

# N-puzzle: a square grid of tiles 0 to N-1, where 0 is the empty square. A tile next to the empty
# square may slide into it. We find a sequence of exactly N_STEPS states that goes from the start
# state to the end state; each step moves the empty square to a neighbouring square.
start = data.puzzle_start
end = data.puzzle_end
steps_count = data.N_STEPS
g = len(start)
N = g * g
T = steps_count

# the start and end states, flattened row by row
flat_start = [start[q // g][q % g] for q in range(N)]
flat_end = [end[q // g][q % g] for q in range(N)]

# steps[t][r][c] is the tile at row r, column c in state t, with 0 for the empty square
steps = VarArray(size=[T, g, g], dom=range(N))

# cells is the same states flattened: cells[t * N + q] is the tile at square q in state t
cells = VarArray(size=T * N, dom=range(N))

# blank[t] is the square of the empty tile in state t
blank = VarArray(size=T, dom=range(N))

# squares that share an edge
adjacent = [(p, q) for p in range(N) for q in range(N)
            if abs(p // g - q // g) + abs(p % g - q % g) == 1]

satisfy(
    # the first state is the start state
    [cells[q] == flat_start[q] for q in range(N)],
    # the last state is the end state
    [cells[(T - 1) * N + q] == flat_end[q] for q in range(N)],
    # the state is a permutation of the tiles 0 to N-1 in every step
    [AllDifferent([cells[t * N + q] for q in range(N)]) for t in range(T)],
    # the square of the empty tile holds the value 0
    [cells[t * N + blank[t]] == 0 for t in range(T)],
    # the empty square moves to a neighbouring square at each step
    [Table(scope=[blank[t], blank[t + 1]], supports=adjacent) for t in range(T - 1)],
    # a tile moves into the square the empty square leaves
    [imply(blank[t] == q, cells[(t + 1) * N + q] == cells[t * N + blank[t + 1]])
     for t in range(T - 1) for q in range(N)],
    # the other squares keep their tiles from one step to the next
    [Or(blank[t] == q, blank[t + 1] == q, cells[(t + 1) * N + q] == cells[t * N + q])
     for t in range(T - 1) for q in range(N)],
    # the steps view is the flattened state
    [steps[t][r][c] == cells[t * N + r * g + c] for t in range(T) for r in range(g) for c in range(g)],
)
