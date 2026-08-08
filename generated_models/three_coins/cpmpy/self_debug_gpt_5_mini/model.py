
import cpmpy as cp
import json

# Data
num_moves = 3  # Number of moves to make all coins face either all heads or all tails
init = [1, 0, 1]  # Initial configuration of the coins, 1 means tails and 0 means heads
# End of data

# Model definition
model = cp.Model()

# Decision Variables
# states[t][i] is the state of coin i after t moves (0=heads, 1=tails)
n_coins = len(init)
states = cp.intvar(0, 1, shape=(num_moves + 1, n_coins), name="states")

# Constraints
# Initial configuration
for i in range(n_coins):
    model += (states[0, i] == init[i])

# Each move flips exactly one coin: Hamming distance between consecutive states == 1
for t in range(num_moves):
    diff_sum = cp.sum([cp.Abs(states[t, i] - states[t + 1, i]) for i in range(n_coins)])
    model += (diff_sum == 1)

# Final state must be all heads (all 0) or all tails (all 1)
final_sum = cp.sum([states[num_moves, i] for i in range(n_coins)])
model += ((final_sum == 0) | (final_sum == n_coins))

# Solve and print
if model.solve():
    # The problem requested booleans where True means tails (1) and False means heads (0).
    # As per the printing guidelines, we output integers 0/1.
    solution = {'steps': states.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
