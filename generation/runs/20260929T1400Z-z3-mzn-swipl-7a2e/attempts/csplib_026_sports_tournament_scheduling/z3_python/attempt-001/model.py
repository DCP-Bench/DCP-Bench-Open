# Sports tournament scheduling: n teams play over n-1 weeks, each week has n/2
# periods, and a period holds one match (a home team and an away team). Every
# team plays once a week, at most twice in the same period over the whole
# tournament, and meets every other team. Teams are numbered 1..n.
import z3


def build(instance):
    n_teams = instance["n_teams"]
    n_weeks = n_teams - 1
    n_periods = n_teams // 2
    teams = range(1, n_teams + 1)

    solver = z3.Solver()

    # home[w][p], away[w][p] = the team number in the slot
    home = [[z3.Int(f"home_{w}_{p}") for p in range(n_periods)] for w in range(n_weeks)]
    away = [[z3.Int(f"away_{w}_{p}") for p in range(n_periods)] for w in range(n_weeks)]
    for w in range(n_weeks):
        for p in range(n_periods):
            solver.add(home[w][p] >= 1, home[w][p] <= n_teams, away[w][p] >= 1, away[w][p] <= n_teams)
            # a team does not play itself
            solver.add(home[w][p] != away[w][p])

    # every team plays exactly once a week: the n slots of a week (home and away,
    # all periods) hold n different teams
    for w in range(n_weeks):
        solver.add(z3.Distinct(home[w] + away[w]))

    # every team meets every other team at least once, at home or away
    for t1 in teams:
        for t2 in range(t1 + 1, n_teams + 1):
            solver.add(z3.Or([z3.Or(z3.And(home[w][p] == t1, away[w][p] == t2),
                                    z3.And(home[w][p] == t2, away[w][p] == t1))
                              for w in range(n_weeks) for p in range(n_periods)]))

    # a team plays at most twice in the same period over the tournament
    for t in teams:
        for p in range(n_periods):
            solver.add(z3.AtMost(*[z3.Or(home[w][p] == t, away[w][p] == t) for w in range(n_weeks)], 2))

    return solver, {"home": home, "away": away}
