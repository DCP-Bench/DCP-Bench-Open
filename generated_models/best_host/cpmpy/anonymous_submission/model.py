from cpmpy import *
import json

# Guests: Andrew=0, Betty=1, Cara=2, Dave=3, Erica=4, Frank=5
n_guests = 6

# Decision Variables
x = intvar(0, n_guests-1, shape=n_guests, name="x")  # Seating order
conflicts = intvar(0, n_guests, name="conflicts")    # Total number of conflicts

# Model
model = Model()

# Constraint: All guests must be seated exactly once
model += AllDifferent(x)

# Define conflicts
conflict_terms = []
for i in range(n_guests):
    left = (i-1) % n_guests
    right = (i+1) % n_guests
    
    # Andrew (0) can only sit next to Dave (3) and Frank (5)
    andrew_conflict = (x[i] == 0) & ((x[left] != 3) & (x[left] != 5) | (x[right] != 3) & (x[right] != 5))
    
    # Betty (1) can only sit next to Cara (2) and Erica (4)
    betty_conflict = (x[i] == 1) & ((x[left] != 2) & (x[left] != 4) | (x[right] != 2) & (x[right] != 4))
    
    # Cara (2) can only sit next to Betty (1) and Frank (5)
    cara_conflict = (x[i] == 2) & ((x[left] != 1) & (x[left] != 5) | (x[right] != 1) & (x[right] != 5))
    
    # Dave (3) can only sit next to Andrew (0) and Erica (4)
    dave_conflict = (x[i] == 3) & ((x[left] != 0) & (x[left] != 4) | (x[right] != 0) & (x[right] != 4))
    
    # Erica (4) can only sit next to Betty (1) and Dave (3)
    erica_conflict = (x[i] == 4) & ((x[left] != 1) & (x[left] != 3) | (x[right] != 1) & (x[right] != 3))
    
    # Frank (5) can only sit next to Andrew (0) and Cara (2)
    frank_conflict = (x[i] == 5) & ((x[left] != 0) & (x[left] != 2) | (x[right] != 0) & (x[right] != 2))
    
    # Count each violation as a separate conflict
    conflict_terms.append(andrew_conflict)
    conflict_terms.append(betty_conflict)
    conflict_terms.append(cara_conflict)
    conflict_terms.append(dave_conflict)
    conflict_terms.append(erica_conflict)
    conflict_terms.append(frank_conflict)

# Sum all conflicts
model += (conflicts == sum(conflict_terms))

# Objective: minimize conflicts
model.minimize(conflicts)

# Solve
model.solve()

# Print solution
solution = {"x": x.value().tolist()}
print(json.dumps(solution))