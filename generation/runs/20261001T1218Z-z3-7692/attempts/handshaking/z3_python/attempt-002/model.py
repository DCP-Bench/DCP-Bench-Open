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
    def spouses(i, j):
        return i // 2 == j // 2

    # shake[(i, j)] (for i < j) is true if persons i and j shook hands. Handshaking is
    # symmetric (i shakes hands with j exactly when j shakes hands with i), so one Boolean
    # per unordered pair serves both directions. Nobody shakes hands with themselves, and
    # nobody with their spouse, so those pairs have no Boolean.
    shake = {}
    for i in range(n):
        for j in range(i + 1, n):
            if not spouses(i, j):
                shake[(i, j)] = z3.Bool(f"shake_{i}_{j}")

    def hands_of(i):
        """The Booleans of the handshakes person i may have taken part in."""
        return [shake[(min(i, j), max(i, j))] for j in range(n) if j != i and not spouses(i, j)]

    # hil is the number of hands Hilary (person 0) shook.
    hil = z3.Int("hil")

    # has[i][v] is true if person i shook exactly v hands. A person shakes at most n - 2
    # hands: nobody's hand twice, and not their own or their spouse's. Booleans are used
    # for the "all answers are different" constraint because Z3 solves Distinct over sums
    # of Booleans slowly; "each count 0..n-2 is given by exactly one person" is a
    # pseudo-Boolean equality over these literals.
    has = [[z3.Bool(f"has_{i}_{v}") for v in range(n - 1)] for i in range(n)]

    solver = z3.Solver()

    # has[i][v] holds exactly when person i shook v hands.
    for i in range(n):
        lits = [(h, 1) for h in hands_of(i)]
        for v in range(n - 1):
            solver.add(has[i][v] == z3.PbEq(lits, v))
        solver.add(z3.PbEq([(has[i][v], 1) for v in range(n - 1)], 1))

    # Hilary's count is the number of hands Hilary shook.
    solver.add(hil == z3.Sum([z3.If(h, 1, 0) for h in hands_of(0)]))
    solver.add(hil >= 0, hil <= n - 2)

    # All the answers are different, except Hilary's (Hilary is the one who asks): the
    # n - 1 other people give n - 1 different counts out of the n - 1 possible counts
    # 0..n-2, so every count is given by exactly one of them.
    for v in range(n - 1):
        solver.add(z3.PbEq([(has[i][v], 1) for i in range(1, n)], 1))

    return solver, {"hil": hil}
