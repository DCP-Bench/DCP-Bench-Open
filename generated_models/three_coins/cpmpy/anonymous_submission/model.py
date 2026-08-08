# Import libraries
from cpmpy import *
import json

# Parameters
num_moves = 3  # Number of moves to make all coins face either all heads or all tails
init = [1, 0, 1]  # Initial configuration of the coins

# Decision Variables
# Each step is a list of 3 coins (0=tails, 1=heads)
steps = intvar(0, 1, shape=(num_moves+1, 3), name="steps")  # +1 to include initial state

# Model
model = Model()

# Initial state constraint
model += (steps[0] == init)

# Transition constraints between steps
for move in range(num_moves):
    # Exactly one coin changes between steps
    model += sum(steps[move+1][c] != steps[move][c] for c in range(3)) == 1
    # If a coin changes, it must flip (0->1 or 1->0)
    for c in range(3):
        model += (steps[move+1][c] != steps[move][c]).implies(
            (steps[move+1][c] == 1 - steps[move][c])
        )

# Final state must be all heads or all tails
model += (sum(steps[num_moves]) == 0) | (sum(steps[num_moves]) == 3)

# Solve
model.solve()

# Convert 1/0 to True/False before printing
solution = {
    "steps": [[bool(coin) for coin in step] for step in steps.value().tolist()]
}
print(json.dumps(solution))
# End of CPMPy script