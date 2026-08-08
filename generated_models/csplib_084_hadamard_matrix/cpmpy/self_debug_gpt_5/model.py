
import cpmpy as cp
import json

# Data (optional)
l = 9  # Value of l (must be an odd positive integer)
# End of data

# Basic validation
if l <= 0 or l % 2 == 0:
    print("No solution found.")
else:
    m = (l - 1) // 2

    # Model definition
    model = cp.Model()

    # Decision Variables (boolean 0/1, we will map to {-1, +1} for output)
    A01 = cp.boolvar(shape=l, name="A01")  # 1 corresponds to +1, 0 corresponds to -1
    B01 = cp.boolvar(shape=l, name="B01")

    # Constraints

    # Linear sum constraints: sum_i a_i = 1 and sum_i b_i = 1
    # With mapping a_i = 2*A01[i] - 1, this becomes sum(A01) = (l+1)//2
    target_ones = (l + 1) // 2
    model += (cp.sum(A01) == target_ones)
    model += (cp.sum(B01) == target_ones)

    # Quadratic PAF constraints transformed via XOR:
    # For each s in 1..m:
    # sum_i XOR(A01[i], A01[(i+s)%l]) + sum_i XOR(B01[i], B01[(i+s)%l]) == l+1
    for s in range(1, m + 1):
        xa = cp.sum([A01[i] != A01[(i + s) % l] for i in range(l)])
        xb = cp.sum([B01[i] != B01[(i + s) % l] for i in range(l)])
        model += (xa + xb == l + 1)

    # Solve and print
    if model.solve():
        # Map 0/1 booleans to -1/+1
        a_vals = [int(2 * int(A01[i].value()) - 1) for i in range(l)]
        b_vals = [int(2 * int(B01[i].value()) - 1) for i in range(l)]
        solution = {'a': a_vals, 'b': b_vals}
        print(json.dumps(solution, indent=4))
    else:
        print("No solution found.")
