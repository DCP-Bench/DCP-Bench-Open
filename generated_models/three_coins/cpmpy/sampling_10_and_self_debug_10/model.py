
import cpmpy as cp
import json

# Data
num_moves = 3
init = [1, 0, 1]  # 1 = tails, 0 = heads (given order tails, heads, tails)

# Model definition
model = cp.Model()

# Decision Variables
# steps[i][j] = 1 if coin j is flipped at move i, else 0
steps = cp.intvar(0, 1, shape=(num_moves, 3), name="steps")

# coins[i][j] = state of coin j after move i (0=heads, 1=tails)
coins = cp.intvar(0, 1, shape=(num_moves + 1, 3), name="coins")

# Initial configuration
model += (coins[0, :] == init)

# State transition: flipping coin j toggles its state
for i in range(num_moves):
    for j in range(3):
        # coin state after flip: coins[i+1,j] = coins[i,j] xor steps[i,j]
        model += (coins[i+1, j] == coins[i, j] + steps[i, j] - 2*(coins[i, j]*steps[i, j]))

# At the end, all coins face same side: all heads (0) or all tails (1)
# We enforce all equal coins[num_moves, :]
model += ( (coins[num_moves, 0] == coins[num_moves, 1]) & 
           (coins[num_moves, 1] == coins[num_moves, 2]) )

# Solve the model
if model.solve():
    solution = {'steps': steps.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
