"""Encodings PuLP lacks as operators: not-equal, absolute value, element, reification."""
import pulp

prob = pulp.LpProblem("encodings", pulp.LpMinimize)
a = prob.add_variable("a", lowBound=0, upBound=5, cat="Integer")
b = prob.add_variable("b", lowBound=0, upBound=5, cat="Integer")
d = prob.add_variable("d", lowBound=0, upBound=5, cat="Integer")

# a != b: one of two strict orders holds, chosen by a binary (M = 6 covers the range 0..5).
before = prob.add_variable("before", cat="Binary")
prob += a <= b - 1 + 6 * (1 - before), "a_below_b"
prob += a >= b + 1 - 6 * before, "a_above_b"
prob += a + b >= 7, "sum_at_least_7"

# d = |a - b| from below: the minimisation pulls d down to the true absolute value.
prob += d >= a - b
prob += d >= b - a
prob += d  # objective: minimise |a - b|

# element: v = TABLE[idx] with idx a decision, via one indicator per index.
TABLE = [10, 3, 7, 3, 9]
idx = prob.add_variable("idx", lowBound=0, upBound=len(TABLE) - 1, cat="Integer")
v = prob.add_variable("v", lowBound=0, upBound=10, cat="Integer")
choose = prob.add_variable_dicts("choose", range(len(TABLE)), cat="Binary")
prob += pulp.lpSum(choose[j] for j in range(len(TABLE))) == 1
prob += idx == pulp.lpSum(j * choose[j] for j in range(len(TABLE)))
prob += v == pulp.lpSum(TABLE[j] * choose[j] for j in range(len(TABLE)))
prob += v >= 7, "value_at_least_7"
prob += v <= 8, "value_at_most_8"  # only TABLE[2] = 7 lies in 7..8, so idx is unique

# Reification: flag = 1 if and only if x >= 3 (x in 0..5, so M = 3 is enough).
x = prob.add_variable("x", lowBound=0, upBound=5, cat="Integer")
flag = prob.add_variable("flag", cat="Binary")
prob += x >= 3 - 3 * (1 - flag), "flag_implies_x_at_least_3"
prob += x <= 2 + 3 * flag, "x_at_least_3_implies_flag"
prob += x == 4, "fix_x"

status = prob.solve(pulp.PULP_CBC_CMD(msg=False))
print("Status:", pulp.LpStatus[status])
if prob.sol_status == pulp.LpSolutionOptimal:
    print("min |a-b| =", round(pulp.value(d)), f"(a={round(a.varValue)}, b={round(b.varValue)})")
    print("element value =", round(pulp.value(v)), "at index", round(pulp.value(idx)))
    print("flag =", round(pulp.value(flag)))
