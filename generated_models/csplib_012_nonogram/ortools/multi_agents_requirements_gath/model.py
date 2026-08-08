import json
from ortools.sat.python import cp_model

# -------------------------------------------------------------
# Input data (exactly as provided)
# -------------------------------------------------------------
rows = 8  # Number of rows
row_rule_len = 2  # Maximum length of row rules
row_rules = [
    [0, 1],
    [0, 2],
    [4, 4],
    [0, 12],
    [0, 8],
    [0, 9],
    [3, 4],
    [2, 2]
]  # Rules for rows

cols = 13  # Number of columns
col_rule_len = 2  # Maximum length of column rules
col_rules = [
    [0, 2],
    [2, 1],
    [3, 2],
    [0, 6],
    [1, 4],
    [0, 3],
    [0, 4],
    [0, 4],
    [0, 4],
    [0, 5],
    [0, 4],
    [1, 3],
    [0, 2]
]  # Rules for columns

# -------------------------------------------------------------
# Helper: generate all 0/1 sequences of a fixed length that
#         satisfy a given nonogram clue (list of block lengths).
# -------------------------------------------------------------

def generate_sequences(line_len, clue):
    """Return a list of 0/1 lists of length line_len that satisfy the clue.
    The clue is a list that may contain zeros; zeros are ignored.
    """
    blocks = [l for l in clue if l > 0]
    sequences = []

    if not blocks:
        sequences.append([0] * line_len)
        return sequences

    total_blocks_len = sum(blocks)
    m = len(blocks)

    # Recursive search over placements.
    def search(idx, pos, seq):
        # idx: which block we are placing next
        # pos: earliest index in the line we may place the next block start
        # seq: list with the already decided part of the sequence (length len(seq))
        if idx == m:
            # No more blocks; fill the rest with zeros and record sequence
            if len(seq) < line_len:
                seq = seq + [0] * (line_len - len(seq))
            sequences.append(seq)
            return

        L = blocks[idx]

        # Remaining minimal length required for this block and the later ones
        remaining_blocks_len = sum(blocks[idx:])
        remaining_gaps = (m - idx - 1)  # one mandatory zero gap after each block except the last

        max_start = line_len - (remaining_blocks_len + remaining_gaps)
        for start in range(pos, max_start + 1):
            # Fill zeros up to 'start'
            new_seq = seq + [0] * (start - len(seq))
            # Place the current block (L ones)
            new_seq += [1] * L

            if idx == m - 1:
                # Last block – no mandatory zero afterwards
                search(idx + 1, len(new_seq), new_seq)
            else:
                # Need at least one zero gap
                new_seq_with_gap = new_seq + [0]
                search(idx + 1, len(new_seq_with_gap), new_seq_with_gap)

    search(0, 0, [])
    return sequences

# -------------------------------------------------------------
# Build CP-SAT model
# -------------------------------------------------------------
model = cp_model.CpModel()

# Decision variables: board[i][j] in {0,1}
board = [[model.NewBoolVar(f"b_{i}_{j}") for j in range(cols)] for i in range(rows)]

# Row constraints using AllowedAssignments (table constraint)
for i in range(rows):
    allowed = [tuple(seq) for seq in generate_sequences(cols, row_rules[i])]
    model.AddAllowedAssignments(board[i], allowed)

# Column constraints – need to collect variables column-wise first
for j in range(cols):
    col_vars = [board[i][j] for i in range(rows)]
    allowed = [tuple(seq) for seq in generate_sequences(rows, col_rules[j])]
    model.AddAllowedAssignments(col_vars, allowed)

# No objective (pure feasibility)
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 10.0  # just a safeguard
status = solver.Solve(model)

# -------------------------------------------------------------
# Output
# -------------------------------------------------------------
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    solution_board = [[int(solver.Value(board[i][j])) for j in range(cols)] for i in range(rows)]
    print(json.dumps({"board": solution_board}))
else:
    # If somehow infeasible (should not happen with correct clues), print empty board
    print(json.dumps({"board": []}))