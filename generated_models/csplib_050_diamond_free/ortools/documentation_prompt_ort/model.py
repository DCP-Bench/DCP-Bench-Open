from ortools.sat.python import cp_model
import json

N = 10  # Number of vertices in the graph

# Model definition
model = cp_model.CpModel()

# Decision variables
# degrees[i]: degree of vertex i, domain: positive multiples of 3 up to N-1 (max degree in simple graph)
max_degree = N - 1
degrees = [model.NewIntVar(3, max_degree, f'degree_{i}') for i in range(N)]

# Enforce degrees to be multiples of 3
for d in degrees:
    # d % 3 == 0
    mod3 = model.NewIntVar(0, 2, '')
    model.AddModuloEquality(mod3, d, 3)
    model.Add(mod3 == 0)

# Enforce non-increasing order: d_i >= d_{i+1}
for i in range(N - 1):
    model.Add(degrees[i] >= degrees[i + 1])

# Sum of degrees modulo 12 == 0
sum_degrees = model.NewIntVar(0, N * max_degree, 'sum_degrees')
model.Add(sum_degrees == sum(degrees))
mod12 = model.NewIntVar(0, 11, 'mod12')
model.AddModuloEquality(mod12, sum_degrees, 12)
model.Add(mod12 == 0)

# Adjacency matrix variables: matrix[i][j] = 1 if edge exists, else 0
matrix = []
for i in range(N):
    row = []
    for j in range(N):
        if i == j:
            # No loops
            row.append(model.NewIntVar(0, 0, f'matrix_{i}_{j}'))
        else:
            row.append(model.NewBoolVar(f'matrix_{i}_{j}'))
    matrix.append(row)

# Symmetry: matrix[i][j] == matrix[j][i]
for i in range(N):
    for j in range(i + 1, N):
        model.Add(matrix[i][j] == matrix[j][i])

# Degree constraints: sum of edges incident on vertex i == degrees[i]
for i in range(N):
    model.Add(sum(matrix[i][j] for j in range(N)) == degrees[i])

# Diamond-free constraint:
# For every set of 4 distinct vertices, the number of edges among them <= 4
# Number of edges among 4 vertices = sum of edges between all pairs in the 4 vertices
# There are 6 pairs in 4 vertices: (4 choose 2) = 6
from itertools import combinations

quadruples = list(combinations(range(N), 4))
for quad in quadruples:
    edges_in_quad = []
    for (u, v) in combinations(quad, 2):
        edges_in_quad.append(matrix[u][v])
    model.Add(sum(edges_in_quad) <= 4)

# Solve and print all unique degree sequences and one corresponding adjacency matrix each
solver = cp_model.CpSolver()

# To store found degree sequences to avoid duplicates
found_degree_sequences = set()

class SolutionPrinter(cp_model.CpSolverSolutionCallback):
    def __init__(self, degrees, matrix):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.degrees = degrees
        self.matrix = matrix
        self.solutions = 0

    def on_solution_callback(self):
        deg_seq = tuple(self.Value(d) for d in self.degrees)
        if deg_seq in found_degree_sequences:
            return
        found_degree_sequences.add(deg_seq)
        self.solutions += 1

        adj_matrix = []
        for i in range(N):
            row = [self.Value(self.matrix[i][j]) for j in range(N)]
            adj_matrix.append(row)

        solution = {
            'degree_sequence': list(deg_seq),
            'matrix': adj_matrix
        }
        print(json.dumps(solution, indent=4))

# Search for all solutions
solution_printer = SolutionPrinter(degrees, matrix)
status = solver.SearchForAllSolutions(model, solution_printer)

if solution_printer.solutions == 0:
    print("No solution found.")