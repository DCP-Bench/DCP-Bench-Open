
import cpmpy as cp
import json

# Variables for each letter
S = cp.intvar(0, 9, name='S')
E = cp.intvar(0, 9, name='E')
N = cp.intvar(0, 9, name='N')
D = cp.intvar(0, 9, name='D')
M = cp.intvar(0, 9, name='M')
O = cp.intvar(0, 9, name='O')
R = cp.intvar(0, 9, name='R')
Y = cp.intvar(0, 9, name='Y')

letters = [S, E, N, D, M, O, R, Y]

model = cp.Model()

# Constraints
# First letters cannot be zero
model += S != 0
model += M != 0

# All letters must be unique
model += cp.AllDifferent(letters)

# Equation constraint: SEND + MORE = MONEY
send = 1000*S + 100*E + 10*N + D
more = 1000*M + 100*O + 10*R + E
money = 10000*M + 1000*O + 100*N + 10*E + Y
model += send + more == money

# Solve and print the solution
if model.solve():
    solution = {
        's': int(S.value()),
        'e': int(E.value()),
        'n': int(N.value()),
        'd': int(D.value()),
        'm': int(M.value()),
        'o': int(O.value()),
        'r': int(R.value()),
        'y': int(Y.value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
