import cpmpy as cp
import numpy as np
import json

# Step 1: Deconstruct & Pre-compute
# Nonogram problem: Fill grid so that consecutive shaded blocks match row/column rules
# Rules specify block sizes with gaps between them

# Input data
rows = 8
cols = 13
row_rules = [
    [0, 1], [0, 2], [4, 4], [0, 12], [0, 8], [0, 9], [3, 4], [2, 2]
]
col_rules = [
    [0, 2], [2, 1], [3, 2], [0, 6], [1, 4], [0, 3], [0, 4], [0, 4], 
    [0, 4], [0, 5], [0, 4], [1, 3], [0, 2]
]

# Clean rules by removing zeros (padding)
def clean_rules(rules):
    return [[x for x in rule if x > 0] for rule in rules]

clean_row_rules = clean_rules(row_rules)
clean_col_rules = clean_rules(col_rules)

# Step 2: Model with CPMpy
# Decision variables: board[i][j] = 1 if cell (i,j) is shaded, 0 otherwise
board = cp.boolvar(shape=(rows, cols), name="board")

model = cp.Model()

# Function to generate all valid patterns for a line given its rules
def generate_patterns(length, blocks):
    """Generate all valid ways to place blocks in a line of given length"""
    if not blocks:
        return [[0] * length]  # Empty line
    
    patterns = []
    
    def place_blocks(pos, block_idx, current_pattern):
        if block_idx == len(blocks):
            # All blocks placed, fill rest with zeros
            patterns.append(current_pattern + [0] * (length - len(current_pattern)))
            return
        
        block_size = blocks[block_idx]
        min_space_needed = sum(blocks[block_idx+1:]) + len(blocks) - block_idx - 1
        
        # Try all possible positions for this block
        for start in range(pos, length - block_size - min_space_needed + 1):
            # Add zeros before the block
            new_pattern = current_pattern + [0] * (start - len(current_pattern))
            # Add the block
            new_pattern += [1] * block_size
            
            if block_idx < len(blocks) - 1:
                # Add at least one gap after the block (except for last block)
                new_pattern += [0]
                place_blocks(len(new_pattern), block_idx + 1, new_pattern)
            else:
                # Last block, no mandatory gap
                place_blocks(len(new_pattern), block_idx + 1, new_pattern)
    
    place_blocks(0, 0, [])
    return patterns

# Generate patterns for each row and column
row_patterns = []
for i, blocks in enumerate(clean_row_rules):
    patterns = generate_patterns(cols, blocks)
    row_patterns.append(patterns)

col_patterns = []
for j, blocks in enumerate(clean_col_rules):
    patterns = generate_patterns(rows, blocks)
    col_patterns.append(patterns)

# Add constraints using Table constraint for each row and column
for i in range(rows):
    # Each row must match one of its valid patterns
    row_vars = [board[i, j] for j in range(cols)]
    model += cp.Table(row_vars, row_patterns[i])

for j in range(cols):
    # Each column must match one of its valid patterns
    col_vars = [board[i, j] for i in range(rows)]
    model += cp.Table(col_vars, col_patterns[j])

# Step 3: Solve and verify
if model.solve():
    # Extract solution
    solution_board = board.value().tolist()
    
    # Convert to integers (0/1) for JSON output
    solution_board = [[int(cell) for cell in row] for row in solution_board]
    
    # Verification - independent check of the solution
    def verify_solution(board, row_rules, col_rules):
        """Verify that the board satisfies all nonogram constraints"""
        
        def get_blocks_from_line(line):
            """Extract block sizes from a line of 0s and 1s"""
            blocks = []
            current_block = 0
            
            for cell in line:
                if cell == 1:
                    current_block += 1
                else:
                    if current_block > 0:
                        blocks.append(current_block)
                        current_block = 0
            
            if current_block > 0:
                blocks.append(current_block)
            
            return blocks
        
        def clean_rule(rule):
            """Remove zeros from rule"""
            return [x for x in rule if x > 0]
        
        # Check row constraints
        for i, rule in enumerate(row_rules):
            expected_blocks = clean_rule(rule)
            actual_blocks = get_blocks_from_line(board[i])
            
            if actual_blocks != expected_blocks:
                return False, f"Row {i} failed: expected {expected_blocks}, got {actual_blocks}"
        
        # Check column constraints
        for j, rule in enumerate(col_rules):
            expected_blocks = clean_rule(rule)
            column = [board[i][j] for i in range(len(board))]
            actual_blocks = get_blocks_from_line(column)
            
            if actual_blocks != expected_blocks:
                return False, f"Column {j} failed: expected {expected_blocks}, got {actual_blocks}"
        
        return True, "All constraints satisfied"
    
    # Verify the solution
    valid, msg = verify_solution(solution_board, row_rules, col_rules)
    assert valid, f"Verification failed: {msg}"
    
    # Step 4: Output
    solution = {"board": solution_board}
    print(json.dumps(solution))
else:
    print(json.dumps({"error": "No solution found"}))