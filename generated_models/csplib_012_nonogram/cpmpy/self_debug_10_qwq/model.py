
import cpmpy as cp
import json

rows = 8
row_rule_len = 2
row_rules = [
    [0, 1],
    [0, 2],
    [4, 4],
    [0, 12],
    [0, 8],
    [0, 9],
    [3, 4],
    [2, 2]
]
cols = 13
col_rule_len = 2
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
]

board = cp.boolvar(shape=(rows, cols), name="board")
model = cp.Model()

def build_transition_table(blocks, n_cells):
    trans = []
    current_state = 0  # initial state
    initial = current_state
    final = None
    states = set()
    states.add(current_state)
    
    for block in blocks:
        after_state = current_state + block + 1
        # Transition to enter the block:
        trans.append( (current_state, 1, current_state + 1) )
        trans.append( (current_state, 0, current_state) )
        states.add(current_state + 1)
        
        for r in range(block, 0, -1):
            s = current_state + (block - r + 1)
            next_s = s + 1
            trans.append( (s, 1, next_s) )
            trans.append( (s, 0, after_state) )
            states.add(s)
            states.add(next_s)
        
        # After_state transitions
        trans.append( (after_state, 0, after_state) )
        trans.append( (after_state, 1, after_state + 1) )
        states.add(after_state)
        states.add(after_state + 1)
        
        current_state = after_state
    
    final = current_state
    # Add final state transitions
    trans.append( (final, 0, final) )
    
    return (trans, initial, final)

# Add row constraints
for row in range(rows):
    blocks = [x for x in row_rules[row] if x != 0]
    if not blocks:
        model += cp.all(board[row, :] == 0)
        continue
    trans, initial, final = build_transition_table(blocks, cols)
    states = cp.intvar(0, final, shape=cols)
    model += (states[0] == initial)
    model += (states[-1] == final)
    for i in range(cols - 1):
        prev_state = states[i]
        current_cell = board[row, i]  # Fixed: use i instead of i+1
        next_state = states[i+1]
        model += cp.Table([prev_state, current_cell, next_state], trans)

# Add column constraints
for col in range(cols):
    blocks = [x for x in col_rules[col] if x != 0]
    if not blocks:
        model += cp.all(board[:, col] == 0)
        continue
    trans, initial, final = build_transition_table(blocks, rows)
    states = cp.intvar(0, final, shape=rows)
    model += (states[0] == initial)
    model += (states[-1] == final)
    for i in range(rows - 1):
        prev_state = states[i]
        current_cell = board[i+1, col]
        next_state = states[i+1]
        model += cp.Table([prev_state, current_cell, next_state], trans)

if model.solve():
    solution = {'board': board.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
