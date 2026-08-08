
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Data
# Indexing people: 0=Jocelyn, 1=Hilary, and 2..9 are the four guest couples
N = 10
couples = [(0,1), (2,3), (4,5), (6,7), (8,9)]  # (Jocelyn, Hilary) + 4 guest couples

# Decision Variables
H = cp.boolvar(shape=(N, N), name="H")        # handshake matrix
D = cp.intvar(0, 8, shape=N, name="D")        # handshake counts for each person

# Constraints
# No one shakes hands with themselves
for i in range(N):
    model += (H[i, i] == 0)

# Symmetry of handshakes
for i in range(N):
    for j in range(i+1, N):
        model += (H[i, j] == H[j, i])

# No one shakes hands with their spouse
for (a, b) in couples:
    model += (H[a, b] == 0)
    model += (H[b, a] == 0)

# Define handshake counts
for i in range(N):
    model += (D[i] == cp.sum(H[i, :]))

# All answers from the nine people Jocelyn asked (everyone except Jocelyn) are different
model += cp.AllDifferent([D[i] for i in range(1, N)])

# Solve and print
if model.solve():
    hil = int(D[1].value())
    solution = {'hil': hil}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
