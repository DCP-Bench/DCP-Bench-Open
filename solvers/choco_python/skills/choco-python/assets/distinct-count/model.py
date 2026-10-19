from pychoco.model import Model

# Graph: a 5-cycle with a chord, so 3 colours are needed.
N = 5
EDGES = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0), (0, 2)]
K = N  # enough colours for any graph

model = Model()
colour = [model.intvar(0, K - 1, name=f"c{i}") for i in range(N)]
for u, v in EDGES:
    model.arithm(colour[u], "!=", colour[v]).post()

# used[k] is 1 exactly when some node takes colour k. Counting the used
# colours is then a sum over those Booleans, not a count of colour values.
used = [model.boolvar(name=f"used{k}") for k in range(K)]
for i in range(N):
    for k in range(K):
        model.if_then(model.arithm(colour[i], "=", k).reify(), model.arithm(used[k], "=", 1))
count = model.intvar(0, K, name="count")
model.sum(used, "=", count).post()

solution = model.get_solver().find_optimal_solution(count, False)
print("Colours used:", solution.get_int_val(count))
print("Colours:", [solution.get_int_val(c) for c in colour])
