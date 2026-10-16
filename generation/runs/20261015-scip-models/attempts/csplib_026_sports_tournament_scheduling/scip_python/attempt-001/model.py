# Sports tournament scheduling: schedule n teams over n-1 weeks, each week split into n/2 periods with a home and an away slot, so every pair of teams meets exactly once.
from pyscipopt import Model, quicksum


def build(instance):
    n = instance["n_teams"]  # number of teams
    weeks = n - 1  # the tournament lasts n-1 weeks
    periods = n // 2  # each week is divided into n/2 periods

    m = Model()

    # play[i, j, w, p] = 1 if team i plays at home against team j in week w, period p
    play = {}
    for i in range(n):
        for j in range(n):
            if i != j:
                for w in range(weeks):
                    for p in range(periods):
                        play[i, j, w, p] = m.addVar(name=f"play_{i}_{j}_{w}_{p}", vtype="B")

    # team t plays at home (resp. away) in week w, period p
    def home(t, w, p):
        return quicksum(play[t, j, w, p] for j in range(n) if j != t)

    def away(t, w, p):
        return quicksum(play[i, t, w, p] for i in range(n) if i != t)

    # team t plays in week w, period p, at either slot
    def plays(t, w, p):
        return home(t, w, p) + away(t, w, p)

    # every period holds exactly one game: its home slot and its away slot are each filled once
    for w in range(weeks):
        for p in range(periods):
            m.addCons(quicksum(home(t, w, p) for t in range(n)) == 1)
            m.addCons(quicksum(away(t, w, p) for t in range(n)) == 1)

    # every team plays once a week
    for t in range(n):
        for w in range(weeks):
            m.addCons(quicksum(plays(t, w, p) for p in range(periods)) == 1)

    # every team plays at most twice in the same period over the tournament
    for t in range(n):
        for p in range(periods):
            m.addCons(quicksum(plays(t, w, p) for w in range(weeks)) <= 2)

    # every team plays every other team exactly once
    for i in range(n):
        for j in range(i + 1, n):
            m.addCons(
                quicksum(play[i, j, w, p] + play[j, i, w, p]
                         for w in range(weeks) for p in range(periods)) == 1
            )

    # outputs: the team in each home and away slot, numbered from 1
    home_out = [[quicksum((t + 1) * home(t, w, p) for t in range(n)) for p in range(periods)]
                for w in range(weeks)]
    away_out = [[quicksum((t + 1) * away(t, w, p) for t in range(n)) for p in range(periods)]
                for w in range(weeks)]

    return m, {"home": home_out, "away": away_out}
