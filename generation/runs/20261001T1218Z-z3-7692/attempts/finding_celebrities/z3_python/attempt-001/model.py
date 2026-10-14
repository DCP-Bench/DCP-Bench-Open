# Finding celebrities: in a party, a celebrity is known by everybody and knows only
# celebrities. Find who the celebrities are.
import z3


def build(instance):
    graph = instance["graph"]  # graph[i][j] = 1 if person i knows person j
    n = len(graph)

    # celebrities[i] is true if person i is a celebrity.
    celebrities = [z3.Bool(f"celebrities_{i}") for i in range(n)]
    # Number of celebrities; at least one celebrity is present at the party.
    num_celebrities = z3.Int("num_celebrities")

    solver = z3.Solver()

    solver.add(num_celebrities >= 1, num_celebrities <= n)
    solver.add(num_celebrities == z3.Sum([z3.If(c, 1, 0) for c in celebrities]))

    # A person is a celebrity exactly when everybody knows them (the whole column i of the
    # graph is 1, the diagonal included, as in the reference) and the number of people they
    # know equals the number of celebrities, so they know only celebrities.
    for i in range(n):
        known_by = sum(graph[j][i] for j in range(n))  # how many people know i
        knows = sum(graph[i][j] for j in range(n))      # how many people i knows
        # known_by and knows are constants, so the first test is a Python bool.
        everybody_knows_i = (known_by == n)
        solver.add(celebrities[i] == z3.And(z3.BoolVal(everybody_knows_i), num_celebrities == knows))

    return solver, {"celebrities": celebrities}
