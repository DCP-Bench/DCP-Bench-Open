import cpmpy as cp
import numpy as np
import json

# Step 1: Deconstruct & Pre-compute
# Problem: Who killed Agatha in Dreadsbury Mansion?
# People: 0=Agatha, 1=butler, 2=Charles
# Constraints:
# 1. A killer always hates, and is no richer than his victim
# 2. Charles hates noone that Agatha hates
# 3. Agatha hates everybody except the butler
# 4. The butler hates everyone not richer than Aunt Agatha
# 5. The butler hates everyone whom Agatha hates
# 6. Noone hates everyone
# 7. Exactly one person killed Agatha

names = ["Agatha herself", "the butler", "Charles"]
n = 3  # Number of people
AGATHA, BUTLER, CHARLES = 0, 1, 2

# Step 2: Model with CPMpy
model = cp.Model()

# Decision variables
# hates[i][j] = 1 if person i hates person j
hates = cp.boolvar(shape=(n, n), name="hates")

# richer[i][j] = 1 if person i is richer than person j
richer = cp.boolvar(shape=(n, n), name="richer")

# killed[i] = 1 if person i killed Agatha
killed = cp.boolvar(shape=n, name="killed")

# Constraint 1: A killer always hates, and is no richer than his victim (Agatha)
for i in range(n):
    # If person i killed Agatha, then i hates Agatha AND i is not richer than Agatha
    model += killed[i].implies(hates[i][AGATHA])
    model += killed[i].implies(~richer[i][AGATHA])

# Constraint 2: Charles hates noone that Agatha hates
for j in range(n):
    model += hates[AGATHA][j].implies(~hates[CHARLES][j])

# Constraint 3: Agatha hates everybody except the butler
model += hates[AGATHA][AGATHA] == 1  # Agatha hates herself
model += hates[AGATHA][BUTLER] == 0  # Agatha does NOT hate the butler
model += hates[AGATHA][CHARLES] == 1  # Agatha hates Charles

# Constraint 4: The butler hates everyone not richer than Aunt Agatha
for i in range(n):
    model += (~richer[i][AGATHA]).implies(hates[BUTLER][i])

# Constraint 5: The butler hates everyone whom Agatha hates
for j in range(n):
    model += hates[AGATHA][j].implies(hates[BUTLER][j])

# Constraint 6: Noone hates everyone
for i in range(n):
    # Person i does not hate everyone, so there exists someone j that i doesn't hate
    model += cp.sum([~hates[i][j] for j in range(n)]) >= 1

# Constraint 7: Exactly one person killed Agatha
model += cp.sum(killed) == 1

# Step 3: Solve and verify
if model.solve():
    # Extract the solution
    killer_index = None
    for i in range(n):
        if killed.value()[i] == 1:
            killer_index = i
            break
    
    # Verification
    def verify_solution(killer_idx, hates_matrix, richer_matrix):
        """Verify the solution satisfies all constraints"""
        h = hates_matrix
        r = richer_matrix
        
        # Check constraint 1: Killer hates and is not richer than victim
        if not (h[killer_idx][AGATHA] and not r[killer_idx][AGATHA]):
            return False
        
        # Check constraint 2: Charles hates noone that Agatha hates
        for j in range(n):
            if h[AGATHA][j] and h[CHARLES][j]:
                return False
        
        # Check constraint 3: Agatha hates everybody except the butler
        if not (h[AGATHA][AGATHA] and not h[AGATHA][BUTLER] and h[AGATHA][CHARLES]):
            return False
        
        # Check constraint 4: Butler hates everyone not richer than Agatha
        for i in range(n):
            if not r[i][AGATHA] and not h[BUTLER][i]:
                return False
        
        # Check constraint 5: Butler hates everyone whom Agatha hates
        for j in range(n):
            if h[AGATHA][j] and not h[BUTLER][j]:
                return False
        
        # Check constraint 6: Noone hates everyone
        for i in range(n):
            if sum(h[i]) == n:
                return False
        
        return True
    
    assert verify_solution(killer_index, hates.value(), richer.value()), "Solution verification failed!"
    
    # Step 4: Output
    solution = {"killer": killer_index}
    print(json.dumps(solution))
else:
    print(json.dumps({"error": "No solution found"}))