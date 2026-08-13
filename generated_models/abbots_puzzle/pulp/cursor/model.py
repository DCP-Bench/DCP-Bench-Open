import pulp
import json

prob = pulp.LpProblem("abbots_puzzle", pulp.LpMinimize)

# Decision variables: number of men, women, and children
men = pulp.LpVariable("men", lowBound=0, upBound=100, cat=pulp.LpInteger)
women = pulp.LpVariable("women", lowBound=0, upBound=100, cat=pulp.LpInteger)
children = pulp.LpVariable("children", lowBound=0, upBound=100, cat=pulp.LpInteger)

# 100 people in total
prob += men + women + children == 100
# 100 bushels: 3 per man, 2 per woman, 1/2 per child  (×2 to stay integer)
prob += 6 * men + 4 * women + children == 200
# Five times as many women as men
prob += women == 5 * men

status = prob.solve(pulp.PULP_CBC_CMD(msg=False))
if status not in (pulp.LpStatusOptimal, pulp.LpStatusNotSolved) and pulp.LpStatus[status] != "Optimal":
    if pulp.value(men) is None:
        raise SystemExit(f"No solution found ({pulp.LpStatus[status]}).")

print(json.dumps({
    "men": int(round(pulp.value(men))),
    "women": int(round(pulp.value(women))),
    "children": int(round(pulp.value(children))),
}))
