
import cpmpy as cp
import json

# Data
num_moves = 3  # Number of moves to make all coins face either all heads or all tails
init = [1, 0, 1]  # Initial configuration of the coins, 1 means tails and 0 means heads
# End of data

# Model definition
model = cp.Model()

# Decision Variables
# steps[t][j] is the state of coin j after move t (0=heads, 1=tails)
steps = cp.intvar(0, 1, shape=(num_moves, 3), name="steps")
# flips[t][j] is 1 if coin j is flipped on move t, else 0
flips = cp.intvar(0, 1, shape=(num_moves, 3), name="flips")
# carry[t][j] represents whether prev+flip >= 2 (i.e., both 1) to model modulo 2
carry = cp.intvar(0, 1, shape=(num_moves, 3), name="carry")

# Constraints
for t in range(num_moves):
    # Exactly one coin flipped per move
    model += cp.sum(flips[t, :]) == 1

    for j in range(3):
        if t == 0:
            prev_val = init[j]
            # carry constraints: carry == prev & flip
            model += carry[t, j] <= flips[t, j]
            model += carry[t, j] <= prev_val
            model += carry[t, j] >= prev_val + flips[t, j] - 1
            # steps = (prev + flip) % 2 -> steps = prev + flip - 2*carry
            model += steps[t, j] == prev_val + flips[t, j] - 2 * carry[t, j]
        else:
            # prev is steps[t-1, j]
            prev = steps[t - 1, j]
            model += carry[t, j] <= flips[t, j]
            model += carry[t, j] <= prev
            model += carry[t, j] >= prev + flips[t, j] - 1
            model += steps[t, j] == prev + flips[t, j] - 2 * carry[t, j]

# Final configuration must be all heads (all 0) or all tails (all 1)
final_sum = cp.sum(steps[num_moves - 1, :])
model += (final_sum == 0) | (final_sum == 3)

# Solve and print
if model.solve():
    # As requested, represent booleans as 1 for True (tails) and 0 for False (heads)
    solution = {'steps': steps.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
