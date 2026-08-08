# Import libraries
from cpmpy import *
import json

# Parameters
total_steps = 20  # Total steps to climb
step_sizes = [3, 4, 5]  # Possible step sizes at each move
max_moves = 20  # Maximum possible moves (upper bound)

# Decision Variables
steps = intvar(0, 5, shape=max_moves, name="steps")  # Steps taken at each move (0 means no move)

# Model
model = Model()

# The sum of all steps must equal total_steps
model += sum(steps) == total_steps

# Each step must be either 0 or one of the allowed step sizes
for move in range(max_moves):
    model += (steps[move] == 0) | (steps[move] == 3) | (steps[move] == 4) | (steps[move] == 5)

# After reaching the top, all remaining steps must be 0
for move in range(max_moves - 1):
    model += (steps[move] == 0).implies(steps[move + 1] == 0)

# Solve
model.solve()

# Print solution (filter out trailing zeros and convert to Python int)
solution_steps = [int(step) for step in steps.value() if step != 0]
solution = {
    "steps": solution_steps
}
print(json.dumps(solution))
# End of CPMPy script