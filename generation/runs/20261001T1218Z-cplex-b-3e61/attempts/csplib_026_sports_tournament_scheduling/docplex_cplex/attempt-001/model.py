"""Sports tournament scheduling: schedule a round robin of n teams over n-1 weeks, each week split
into n/2 periods holding one game (a home team against an away team), so that every team plays
once a week, at most twice in the same period over the tournament, and against every other team.

The model reports the home team and the away team of every week and period (teams 1..n).
"""
from docplex.mp.model import Model


def build(instance):
    n_teams = instance["n_teams"]
    n_weeks, n_periods = n_teams - 1, n_teams // 2
    teams = range(1, n_teams + 1)
    slots = [(w, p) for w in range(n_weeks) for p in range(n_periods)]
    pairs = [(t1, t2) for t1 in teams for t2 in teams if t1 < t2]

    model = Model("sports_tournament_scheduling")

    # Every team plays every other team, and there are exactly as many game slots as pairs of
    # teams, so each pair meets exactly once. meet[g, s] = 1 when pair g plays in slot s. A
    # variable per pair and slot (784 at n = 8) is smaller than one per ordered pair and slot.
    meet = {(g, s): model.binary_var(name=f"meet_{g[0]}_{g[1]}_{s[0]}_{s[1]}") for g in pairs for s in slots}

    # Each pair of teams plays once.
    for g in pairs:
        model.add_constraint(model.sum(meet[g, s] for s in slots) == 1)

    # Each slot holds one game, between two different teams.
    for s in slots:
        model.add_constraint(model.sum(meet[g, s] for g in pairs) == 1)

    # Every team plays once a week.
    for w in range(n_weeks):
        for t in teams:
            model.add_constraint(model.sum(meet[g, (w, p)] for g in pairs if t in g
                                           for p in range(n_periods)) == 1)

    # Every team plays at most twice in the same period.
    for p in range(n_periods):
        for t in teams:
            model.add_constraint(model.sum(meet[g, (w, p)] for g in pairs if t in g
                                           for w in range(n_weeks)) <= 2)

    # Who plays at home. lower(s) and upper(s) are the smaller and larger team number of the game
    # in slot s; flip[s] = 1 puts the larger one at home. shift[s] = flip[s] * (upper - lower) is
    # linearised with the standard four inequalities (the difference lies in 1..n-1).
    def lower(s):
        return model.sum(g[0] * meet[g, s] for g in pairs)

    def upper(s):
        return model.sum(g[1] * meet[g, s] for g in pairs)

    shift = {}
    for s in slots:
        f = model.binary_var(name=f"flip_{s[0]}_{s[1]}")
        d = model.integer_var(0, n_teams - 1, name=f"shift_{s[0]}_{s[1]}")
        model.add_constraint(d <= (n_teams - 1) * f)
        model.add_constraint(d >= f)
        model.add_constraint(d <= upper(s) - lower(s) - (1 - f))
        model.add_constraint(d >= upper(s) - lower(s) - (n_teams - 1) * (1 - f))
        shift[s] = d

    # home = lower + shift and away = upper - shift; each output is built as a fresh sum.
    home = [[model.sum([g[0] * meet[g, (w, p)] for g in pairs] + [shift[w, p]])
             for p in range(n_periods)] for w in range(n_weeks)]
    away = [[model.sum([g[1] * meet[g, (w, p)] for g in pairs] + [-1 * shift[w, p]])
             for p in range(n_periods)] for w in range(n_weeks)]

    return model, {"home": home, "away": away}
