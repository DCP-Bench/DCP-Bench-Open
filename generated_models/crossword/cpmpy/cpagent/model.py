import cpmpy as cp
import numpy as np
import json

# Step 1: Deconstruct & Pre-compute
# Words sorted by length (desc) then alphabetically
words_sorted = ["HOSES", "LASER", "SAILS", "SHEET", "STEER", "HEEL", "HIKE", "KEEL", "KNOT", "LINE", "AFT", "ALE", "EEL", "LEE", "TIE"]

# Word lengths required for each position based on crossword structure
required_lengths = {1: 5, 2: 5, 3: 5, 4: 4, 5: 4, 6: 3, 7: 3, 8: 5}

# Group words by length
words_by_length = {}
for i, word in enumerate(words_sorted):
    length = len(word)
    if length not in words_by_length:
        words_by_length[length] = []
    words_by_length[length].append(i)

# Intersections: (pos1, pos2, char_idx1, char_idx2, cell)
# These represent where words cross in the crossword grid
intersections = [
    (1, 2, 2, 0, (0, 2)),  # Word 1 char 2 = Word 2 char 0
    (1, 3, 4, 0, (0, 4)),  # Word 1 char 4 = Word 3 char 0  
    (2, 4, 2, 1, (2, 2)),  # Word 2 char 2 = Word 4 char 1
    (2, 7, 3, 0, (3, 2)),  # Word 2 char 3 = Word 7 char 0
    (2, 8, 4, 2, (4, 2)),  # Word 2 char 4 = Word 8 char 2
    (3, 4, 2, 3, (2, 4)),  # Word 3 char 2 = Word 4 char 3
    (3, 7, 3, 2, (3, 4)),  # Word 3 char 3 = Word 7 char 2
    (3, 8, 4, 4, (4, 4)),  # Word 3 char 4 = Word 8 char 4
    (4, 5, 2, 0, (2, 3)),  # Word 4 char 2 = Word 5 char 0
    (5, 7, 1, 1, (3, 3)),  # Word 5 char 1 = Word 7 char 1
    (5, 8, 2, 3, (4, 3)),  # Word 5 char 2 = Word 8 char 3
    (6, 8, 1, 0, (4, 0))   # Word 6 char 1 = Word 8 char 0
]

# Step 2: Model with CPMpy
# Decision variables: E[i] = index of word assigned to position i+1
E = cp.intvar(0, 14, shape=8, name="E")

model = cp.Model()

# Constraint 1: Each word can only be used once
model += cp.AllDifferent(E)

# Constraint 2: Word length must match position requirement
for pos in range(1, 9):
    valid_words = words_by_length[required_lengths[pos]]
    model += cp.sum([E[pos-1] == word_idx for word_idx in valid_words]) == 1

# Constraint 3: Intersection constraints - characters must match at crossing points
for pos1, pos2, idx1, idx2, cell in intersections:
    # Create allowed combinations where characters match
    allowed_pairs = []
    
    # Get valid words for each position
    valid_words1 = words_by_length[required_lengths[pos1]]
    valid_words2 = words_by_length[required_lengths[pos2]]
    
    for w1_idx in valid_words1:
        for w2_idx in valid_words2:
            word1 = words_sorted[w1_idx]
            word2 = words_sorted[w2_idx]
            
            # Check if characters at intersection match
            if word1[idx1] == word2[idx2]:
                allowed_pairs.append((w1_idx, w2_idx))
    
    # Add table constraint for this intersection
    if allowed_pairs:
        model += cp.Table([E[pos1-1], E[pos2-1]], allowed_pairs)

# Step 3: Solve and verify
if model.solve():
    solution_values = E.value()
    solution = {"E": solution_values.tolist()}
    
    # Verification
    def verify_solution(sol):
        E_vals = sol["E"]
        
        # Check 1: All different words used
        if len(set(E_vals)) != len(E_vals):
            return False, "Not all different words"
        
        # Check 2: Word lengths match position requirements
        for pos in range(1, 9):
            word_idx = E_vals[pos-1]
            word = words_sorted[word_idx]
            required_len = required_lengths[pos]
            if len(word) != required_len:
                return False, f"Position {pos} needs length {required_len}, got {len(word)}"
        
        # Check 3: All intersections have matching characters
        for pos1, pos2, idx1, idx2, cell in intersections:
            word1_idx = E_vals[pos1-1]
            word2_idx = E_vals[pos2-1]
            word1 = words_sorted[word1_idx]
            word2 = words_sorted[word2_idx]
            
            if word1[idx1] != word2[idx2]:
                return False, f"Intersection {pos1}-{pos2}: {word1}[{idx1}]='{word1[idx1]}' != {word2}[{idx2}]='{word2[idx2]}'"
        
        return True, "All constraints satisfied"
    
    valid, msg = verify_solution(solution)
    assert valid, f"Verification failed: {msg}"
    
    # Step 4: Output
    print(json.dumps(solution))
else:
    print(json.dumps({"error": "No solution found"}))