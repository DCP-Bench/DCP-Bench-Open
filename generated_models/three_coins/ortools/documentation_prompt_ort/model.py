from ortools.sat.python import cp_model
import json

# Input data
num_moves = 3  # Number of moves to make all coins face either all heads or all tails
init = [1, 0, 1]  # Initial configuration of the coins (1 = tails, 0 = heads)

# Model definition
model = cp_model.CpModel()

# We have 3 coins, indexed 0,1,2
num_coins = len(init)

# Decision variables:
# steps[m][c] = 1 if coin c is flipped at move m, else 0
steps = []
for m in range(num_moves):
    step_vars = []
    for c in range(num_coins):
        step_vars.append(model.NewBoolVar(f'step_{m}_coin_{c}'))
    steps.append(step_vars)

# After all moves, the coins should be all heads (0) or all tails (1)
# Let's define final state variables for each coin
final_state = []
for c in range(num_coins):
    final_state.append(model.NewBoolVar(f'final_state_coin_{c}'))

# The final state coins are either all 0 or all 1
# We enforce that all final_state are equal
for c in range(1, num_coins):
    model.Add(final_state[c] == final_state[0])

# final_state[0] can be 0 or 1 (heads or tails)
# final_state[c] = init[c] XOR (sum of flips on coin c mod 2)
# sum of flips mod 2 = parity of flips on coin c
for c in range(num_coins):
    # sum flips on coin c
    sum_flips = model.NewIntVar(0, num_moves, f'sum_flips_coin_{c}')
    model.Add(sum_flips == sum(steps[m][c] for m in range(num_moves)))
    # parity variable for flips on coin c
    parity = model.NewBoolVar(f'parity_coin_{c}')
    model.AddModuloEquality(parity, sum_flips, 2)
    # final_state[c] = init[c] XOR parity
    # XOR can be expressed as final_state[c] == init[c] + parity (mod 2)
    if init[c] == 0:
        model.Add(final_state[c] == parity)
    else:
        # final_state[c] == 1 - parity
        model.Add(final_state[c] == 1 - parity)

# No objective, just find a feasible solution
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    # Extract steps as list of lists of 0/1
    steps_sol = []
    for m in range(num_moves):
        step_m = []
        for c in range(num_coins):
            step_m.append(solver.Value(steps[m][c]))
        steps_sol.append(step_m)
    solution = {
        'steps': steps_sol
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")