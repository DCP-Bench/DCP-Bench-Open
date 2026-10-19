from pychoco.model import Model

SUPPLY = [20, 30]                      # per warehouse
DEMAND = [10, 25, 15]                  # per shop; total must equal total supply
COST = [[4, 6, 9],                     # COST[w][s]: cost per unit from warehouse w to shop s
        [5, 3, 7]]

W, S = len(SUPPLY), len(DEMAND)
model = Model()
ship = [[model.intvar(0, min(SUPPLY[w], DEMAND[s]), name=f"x{w}{s}") for s in range(S)] for w in range(W)]
for w in range(W):
    model.sum(ship[w], "<=", SUPPLY[w]).post()
for s in range(S):
    model.sum([ship[w][s] for w in range(W)], "=", DEMAND[s]).post()

cells = [ship[w][s] for w in range(W) for s in range(S)]
weights = [COST[w][s] for w in range(W) for s in range(S)]
total_cost = model.intvar(0, sum(weights) * max(SUPPLY), name="total_cost")
model.scalar(cells, weights, "=", total_cost).post()

solution = model.get_solver().find_optimal_solution(total_cost, False)
if solution is None:
    print("no shipment plan")
else:
    for w in range(W):
        print("warehouse", w, [solution.get_int_val(ship[w][s]) for s in range(S)])
    print("Minimum cost:", solution.get_int_val(total_cost))
