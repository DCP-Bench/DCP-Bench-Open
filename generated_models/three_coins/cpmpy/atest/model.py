from cpmpy import *
import json

# Input data
num_moves = 3  # Number of moves to make all coins face either all heads or all tails
init = [1, 0, 1]  # Initial configuration of the coins (1 = tails, 0 = heads)

# Parameters
n_coins = len(init)  # Number of coins
n_moves = num_moves  # Number of moves

# Decision variables
steps = intvar(0, n_coins - 1, shape=n_moves, name="steps")  # The coin to flip in each move

# Model
model = Model()

# Simulate the flipping process
# We will track the state of the coins after each move
# Let's define a variable to represent the state of the coins after each move
state = intvar(0, 1, shape=(n_moves + 1, n_coins), name="state")

# Initialize the state with the initial configuration
model += [state[0, :] == init]

# Update the state after each move
for move in range(n_moves):
    # Copy the previous state
    model += [state[move + 1, :] == state[move, :]]
    # Flip the coin at the position specified by steps[move]
    model += [state[move + 1, steps[move]] == 1 - state[move, steps[move]]]

# After all moves, all coins must be either all heads or all tails
all_heads = [0] * n_coins
all_tails = [1] * n_coins
model += (state[n_moves, :] == all_heads) | (state[n_moves, :] == all_tails)

# Solve the model
model.solve()

# Print the solution
solution = {"steps": steps.value().tolist()}
print(json.dumps(solution))