# Sports tournament scheduling (CSPLib 26): schedule n teams over n-1 weeks, each week split into
# n/2 periods with a home and an away team per period, so that every team plays once a week,
# every team plays at most twice in the same period, and every team meets every other team.
from exact import Exact


def build(instance):
    n_teams = instance["n_teams"]  # number of teams (even)
    n_weeks = n_teams - 1
    n_periods = n_teams // 2
    teams = range(1, n_teams + 1)  # teams are numbered from 1 to n_teams

    solver = Exact()

    # home[w][p] / away[w][p] = the home / away team in week w, period p
    home = [[f"home_{w}_{p}" for p in range(n_periods)] for w in range(n_weeks)]
    away = [[f"away_{w}_{p}" for p in range(n_periods)] for w in range(n_weeks)]
    # is_home[w][p][t] = 1 when team t is the home team of week w, period p (same for away).
    # Saying that a team plays in a match, or meets another team, talks about the team
    # that fills a slot, so each slot gets one 0/1 variable per team.
    is_home = {}
    is_away = {}
    for w in range(n_weeks):
        for p in range(n_periods):
            solver.addVariable(home[w][p], 1, n_teams)
            solver.addVariable(away[w][p], 1, n_teams)
            for t in teams:
                is_home[w, p, t] = f"home_{w}_{p}_is_{t}"
                is_away[w, p, t] = f"away_{w}_{p}_is_{t}"
                solver.addVariable(is_home[w, p, t], 0, 1)
                solver.addVariable(is_away[w, p, t], 0, 1)
            # a slot has exactly one team, and its number is the value of home / away
            solver.addConstraint([(1, is_home[w, p, t]) for t in teams], True, 1, True, 1)
            solver.addConstraint([(1, is_away[w, p, t]) for t in teams], True, 1, True, 1)
            solver.addConstraint([(t, is_home[w, p, t]) for t in teams] + [(-1, home[w][p])],
                                 True, 0, True, 0)
            solver.addConstraint([(t, is_away[w, p, t]) for t in teams] + [(-1, away[w][p])],
                                 True, 0, True, 0)
            # teams cannot play themselves: home != away
            for t in teams:
                solver.addConstraint([(1, is_home[w, p, t]), (1, is_away[w, p, t])],
                                     False, 0, True, 1)

    # every team plays once a week: the n teams fill the n slots of a week without repeating
    # (all different over the home and away teams of the week)
    for w in range(n_weeks):
        for t in teams:
            solver.addConstraint([(1, is_home[w, p, t]) for p in range(n_periods)]
                                 + [(1, is_away[w, p, t]) for p in range(n_periods)],
                                 True, 1, True, 1)

    # every team plays at most twice in the same period over the tournament
    for t in teams:
        for p in range(n_periods):
            solver.addConstraint([(1, is_home[w, p, t]) for w in range(n_weeks)]
                                 + [(1, is_away[w, p, t]) for w in range(n_weeks)],
                                 False, 0, True, 2)

    # every team plays every other team: for each pair, some slot has one of them at home and
    # the other away. meets[w][p][t1][t2] can be 1 only if both teams are in that slot.
    for t1 in teams:
        for t2 in teams:
            if t1 >= t2:
                continue
            meets = []
            for w in range(n_weeks):
                for p in range(n_periods):
                    name = f"meets_{w}_{p}_{t1}_{t2}"
                    solver.addVariable(name, 0, 1)
                    # both teams are in the slot: (t1 home and t2 away) or (t2 home and t1 away)
                    solver.addConstraint([(1, name), (-1, is_home[w, p, t1]),
                                          (-1, is_away[w, p, t1])], False, 0, True, 0)
                    solver.addConstraint([(1, name), (-1, is_home[w, p, t2]),
                                          (-1, is_away[w, p, t2])], False, 0, True, 0)
                    meets.append((1, name))
            solver.addConstraint(meets, True, 1)

    return solver, {"home": home, "away": away}
