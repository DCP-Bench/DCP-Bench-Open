"""Schedule jobs on one machine (no overlap), minimise the sum of completion times."""
import pulp

NAME = ["A", "B", "C", "D"]
DURATION = [3, 2, 4, 2]
H = sum(DURATION)  # a horizon that bounds every start: the big-M constant

prob = pulp.LpProblem("single_machine", pulp.LpMinimize)
start = prob.add_variable_dicts("start", range(len(NAME)), lowBound=0, upBound=H, cat="Integer")
end = prob.add_variable_dicts("end", range(len(NAME)), lowBound=0, upBound=H, cat="Integer")

for j in range(len(NAME)):
    prob += end[j] == start[j] + DURATION[j], f"length_{NAME[j]}"

# No overlap: for every pair, one of the two orders holds. The binary says which.
for i in range(len(NAME)):
    for j in range(i + 1, len(NAME)):
        i_first = prob.add_variable(f"i_first_{NAME[i]}_{NAME[j]}", cat="Binary")
        prob += end[i] <= start[j] + H * (1 - i_first), f"i_before_j_{NAME[i]}_{NAME[j]}"
        prob += end[j] <= start[i] + H * i_first, f"j_before_i_{NAME[i]}_{NAME[j]}"

prob += pulp.lpSum(end[j] for j in range(len(NAME)))  # the objective: total completion time

status = prob.solve(pulp.PULP_CBC_CMD(msg=False))
print("Status:", pulp.LpStatus[status])
if prob.sol_status == pulp.LpSolutionOptimal:
    for j in sorted(range(len(NAME)), key=lambda j: start[j].varValue):
        print(f"{NAME[j]}: start {round(start[j].varValue)}, end {round(end[j].varValue)}")
    print("Total completion time:", round(pulp.value(prob.objective)))
