"""Magic sequence: find integers x[0..n-1], each between 0 and n-1, such that for
every i the number i occurs exactly x[i] times in the sequence.

For example 6, 2, 1, 0, 0, 0, 1, 0, 0, 0 is a magic sequence of length 10:
0 occurs 6 times, 1 occurs twice, and so on.
"""
import pulp


def build(instance):
    n = instance["n"]  # length of the sequence; its values are 0..n-1

    problem = pulp.LpProblem("magic_sequence", pulp.LpMinimize)

    # holds[j][v] = 1 if position j of the sequence holds the value v
    holds = [[pulp.LpVariable(f"holds_{j}_{v}", cat="Binary") for v in range(n)]
             for j in range(n)]

    # x[j] = the value at position j (declared output), a bounded integer tied
    # to the 0/1 matrix by equality; the bound 0..n-1 is the problem's own.
    x = [pulp.LpVariable(f"x_{j}", 0, n - 1, cat="Integer") for j in range(n)]

    # every position holds exactly one value, and x reads it back
    for j in range(n):
        problem += pulp.lpSum(holds[j]) == 1
        problem += x[j] == pulp.lpSum(v * holds[j][v] for v in range(n))

    # the number i occurs exactly x[i] times in the sequence
    for i in range(n):
        problem += x[i] == pulp.lpSum(holds[j][i] for j in range(n))

    return problem, {"x": x}
