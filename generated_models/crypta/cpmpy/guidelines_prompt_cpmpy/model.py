
import cpmpy as cp
import json

# Data
op1 = list("BAIJJAJIIAHFCFEBBJEA")
op2 = list("DHFGABCDIDBIFFAGFEJE")
res = list("GJEGACDDHFAFJBFIHEEF")

# Reverse for column-wise (least significant digit first)
rop1 = op1[::-1]
rop2 = op2[::-1]
rres = res[::-1]
# End of data

# Model definition
model = cp.Model()

# Decision Variables: mapping letters A-J to digits 0-9
A = cp.intvar(0, 9, name="A")
B = cp.intvar(0, 9, name="B")
C = cp.intvar(0, 9, name="C")
D = cp.intvar(0, 9, name="D")
E = cp.intvar(0, 9, name="E")
F = cp.intvar(0, 9, name="F")
G = cp.intvar(0, 9, name="G")
H = cp.intvar(0, 9, name="H")
I = cp.intvar(0, 9, name="I")
J = cp.intvar(0, 9, name="J")

letters = {'A': A, 'B': B, 'C': C, 'D': D, 'E': E,
           'F': F, 'G': G, 'H': H, 'I': I, 'J': J}

# Carry variables for each column (0 to 20)
c = cp.intvar(0, 1, shape=21, name="c")

# Constraints
# All letters distinct
model += cp.all_distinct(list(letters.values()))

# No leading zeros: first char of each number
model += B != 0  # op1 leads with B
model += D != 0  # op2 leads with D
model += G != 0  # result leads with G

# Carry start and end
model += c[0] == 0
model += c[20] == 0

# Column-wise addition constraints
for i in range(20):
    x1 = letters[rop1[i]]
    x2 = letters[rop2[i]]
    xr = letters[rres[i]]
    # x1 + x2 + c[i] = xr + 10*c[i+1]
    model += x1 + x2 + c[i] == xr + 10 * c[i+1]

# Solve and print
if model.solve():
    solution = {
        'A': int(A.value()),
        'B': int(B.value()),
        'C': int(C.value()),
        'D': int(D.value()),
        'E': int(E.value()),
        'F': int(F.value()),
        'G': int(G.value()),
        'H': int(H.value()),
        'I': int(I.value()),
        'J': int(J.value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
