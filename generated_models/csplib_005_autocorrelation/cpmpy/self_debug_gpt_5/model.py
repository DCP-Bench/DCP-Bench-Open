
import cpmpy as cp
import json

# Data (optional)
n = 10  # Length of the binary sequence
# End of data

# Model definition
model = cp.Model()

# Decision Variables
# Use booleans u in {0,1}, and map to sequence S = 2*u - 1 at the end
u = cp.boolvar(shape=n, name="u")

# Symmetry breaking: fix the first bit to +1 (i.e., u[0] = 1)
model += (u[0] == 1)

# Non-periodic (open) autocorrelation minimization
y_vars = []  # y_k = C_k^2 for each k

for k in range(1, n):
    m_k = n - k  # number of terms in C_k for non-periodic case

    # w_{i,k} = u[i] XOR u[i+k], i = 0..m_k-1
    # Use tuple for shape to ensure array even when m_k==1
    w_k = cp.boolvar(shape=(m_k,), name=f"w_{k}")
    for i in range(m_k):
        model += (w_k[i] == (u[i] ^ u[i + k]))

    # t_k = sum of XORs = number of unequal pairs at lag k
    t_k = cp.intvar(0, m_k, name=f"t_{k}")
    model += (t_k == cp.sum(w_k))

    # y_k = (m_k - 2*t_k)^2, implemented via a table over t_k
    y_k = cp.intvar(0, m_k * m_k, name=f"y_{k}")
    table_pairs = [[t, (m_k - 2 * t) * (m_k - 2 * t)] for t in range(m_k + 1)]
    model += cp.Table([t_k, y_k], table_pairs)

    y_vars.append(y_k)

# Objective: minimize sum of squared autocorrelations
model.minimize(cp.sum(y_vars))

# Solve and print
if model.solve():
    sequence = [int(2 * int(u[i].value()) - 1) for i in range(n)]
    solution = {'sequence': sequence}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
