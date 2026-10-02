# Handshaking: Hilary and Jocelyn, a married couple, invite some couples for dinner. People
# shake hands, but nobody shakes hands with themselves or with their spouse. Jocelyn asks
# everybody how many hands they shook and all the answers are different. How many hands
# did Hilary shake?
import z3


def build(instance):
    num_couples = instance["num_couples"]  # couples invited, not counting Hilary and Jocelyn
    n = 2 + num_couples * 2                # people at the party

    # Couples are placed side by side: person 2k and person 2k + 1 are married. Hilary is
    # person 0 and Jocelyn is person 1.
    # x[i] is the number of hands person i shook; at most n - 2, since a person shakes
    # nobody's hand twice and skips themselves and their spouse.
    x = [z3.Int(f"x_{i}") for i in range(n)]
    hil = x[0]

    # shake[i][j] is true if persons i and j shook hands. Handshaking is symmetric (i shakes
    # hands with j exactly when j shakes hands with i), so one Boolean per unordered
    # pair is used for both directions. Nobody shakes hands with themselves, and
    # nobody with their spouse, so those pairs are constant false.
    def spouses(i, j):
        return i // 2 == j // 2

    shake = {}
    for i in range(n):
        for j in range(i + 1, n):
            shake[(i, j)] = z3.BoolVal(False) if spouses(i, j) else z3.Bool(f"shake_{i}_{j}")

    def hands(i, j):
        return shake[(min(i, j), max(i, j))]

    solver = z3.Solver()

    # x[i] counts the hands person i shook.
    for i in range(n):
        solver.add(x[i] >= 0, x[i] <= n - 2)
        solver.add(x[i] == z3.Sum([z3.If(hands(i, j), 1, 0) for j in range(n) if j != i]))

    # All the answers are different, except Hilary's (Hilary is the one who asks nobody).
    solver.add(z3.Distinct(x[1:]))

    return solver, {"hil": hil}
