
import cpmpy as cp
import json

# Decision Variables
sequence = cp.boolvar(shape=13)  # 0 for male, 1 for female
females_so_far = cp.intvar(0, 9, shape=13)

model = cp.Model()

# Constraints for cumulative females
for i in range(13):
    if i == 0:
        model += (females_so_far[i] == sequence[i])
    else:
        model += (females_so_far[i] == females_so_far[i-1] + sequence[i])

# Total females must be 9
model += (cp.sum(sequence) == 9)

# Ratio constraint at every step: 3*F <=7*M → 3*F <=7*(k+1 - F)
for k in range(13):
    model += (3 * females_so_far[k] <= 7 * ( (k + 1) - females_so_far[k] ) )

# Solve and print
if model.solve():
    # Convert boolean array to integers (0/1)
    sequence_val = [int(x) for x in sequence.value()]
    solution = {'sequence': sequence_val}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
