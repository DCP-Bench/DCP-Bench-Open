import json
from ortools.sat.python import cp_model

# ---------------------------------------------------------------------------
# Model parameters
# ---------------------------------------------------------------------------
NUM_DICE = 5      # Rock, Paper, Scissors, Lizard, Spock
FACES    = 6      # standard cubic dice
FACE_RANGE = (1, 20)  # allowed numbers on a face – upper bound helps the solver

# Required winning orientations (0-based indices)
BEATS = [
    (0, 2),  # Rock    beats Scissors
    (0, 3),  # Rock    beats Lizard
    (1, 0),  # Paper   beats Rock
    (1, 4),  # Paper   beats Spock
    (2, 1),  # Scissors beats Paper
    (2, 3),  # Scissors beats Lizard
    (3, 1),  # Lizard  beats Paper
    (3, 4),  # Lizard  beats Spock
    (4, 0),  # Spock   beats Rock
    (4, 2)   # Spock   beats Scissors
]

TOTAL_PAIRS = FACES * FACES  # 36
MAJORITY    = TOTAL_PAIRS // 2 + 1  # 19  (strictly larger than 0.5)

# ---------------------------------------------------------------------------
# Build CP-SAT model
# ---------------------------------------------------------------------------
model = cp_model.CpModel()

# Dice faces – dice[d][k] is the number printed on face k of die d
low, high = FACE_RANGE
dice = [[model.NewIntVar(low, high, f'die_{d}_face_{k}')
         for k in range(FACES)] for d in range(NUM_DICE)]

# Optional: sort the faces of every die to break internal permutations
for d in range(NUM_DICE):
    for k in range(FACES - 1):
        model.Add(dice[d][k] <= dice[d][k + 1])

# ---------------------------------------------------------------------------
# Helper structures to count pairwise wins
# ---------------------------------------------------------------------------
# wins[i][j] – integer variable in 0..36 counting (face of i) > (face of j)
wins = [[None for _ in range(NUM_DICE)] for _ in range(NUM_DICE)]

# To avoid duplicating comparison variables we work on unordered pairs only
for i in range(NUM_DICE):
    for j in range(i + 1, NUM_DICE):
        greater_bools = []  # face(i)  > face(j)
        smaller_bools = []  # face(i)  < face(j) – symmetric orientation

        for fi in range(FACES):
            for fj in range(FACES):
                gt = model.NewBoolVar(f'gt_{i}_{fi}_{j}_{fj}')
                lt = model.NewBoolVar(f'lt_{i}_{fi}_{j}_{fj}')

                # Exactly one of gt / lt / tie is true.  We implement this with
                #   gt + lt <= 1            (can be a tie)
                model.Add(gt + lt <= 1)

                # Reify the comparison constraints
                model.Add(dice[i][fi] > dice[j][fj]).OnlyEnforceIf(gt)
                model.Add(dice[i][fi] <= dice[j][fj]).OnlyEnforceIf(gt.Not())

                model.Add(dice[i][fi] < dice[j][fj]).OnlyEnforceIf(lt)
                model.Add(dice[i][fi] >= dice[j][fj]).OnlyEnforceIf(lt.Not())

                greater_bools.append(gt)
                smaller_bools.append(lt)

        # Sum up win counters for both orientations of the unordered pair
        win_ij = model.NewIntVar(0, TOTAL_PAIRS, f'wins_{i}_{j}')
        win_ji = model.NewIntVar(0, TOTAL_PAIRS, f'wins_{j}_{i}')
        model.Add(win_ij == sum(greater_bools))
        model.Add(win_ji == sum(smaller_bools))

        wins[i][j] = win_ij
        wins[j][i] = win_ji

        # Exclude the possibility of an exact 50-50 tie (18 wins each)
        model.Add(win_ij != TOTAL_PAIRS // 2)  # i<j implies j>i also ≠18 implicitly

# ---------------------------------------------------------------------------
# Impose the RPSLS dominance relations
# ---------------------------------------------------------------------------
for (i, j) in BEATS:
    # Required winner
    model.Add(wins[i][j] >= MAJORITY)     # strictly > 18
    # Required loser (redundant but strengthens the model)
    model.Add(wins[j][i] <= TOTAL_PAIRS - MAJORITY)  # ≤17

# ---------------------------------------------------------------------------
# Solve
# ---------------------------------------------------------------------------
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 30.0  # safety timeout
solver.parameters.num_search_workers = 8      # parallelism
status = solver.Solve(model)

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    solution = [[int(solver.Value(dice[d][k])) for k in range(FACES)]
                for d in range(NUM_DICE)]
    print(json.dumps({"dice": solution}))
else:
    # Should not happen for reasonable bounds; fallback empty output
    print(json.dumps({"dice": []}))
