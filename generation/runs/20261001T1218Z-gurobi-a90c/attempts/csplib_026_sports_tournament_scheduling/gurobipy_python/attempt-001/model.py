"""Sports tournament scheduling: n teams over n-1 weeks of n/2 periods; every team plays once a week, at most twice in a period, and every other team once."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    n_teams = instance["n_teams"]
    n_weeks, n_periods = n_teams - 1, n_teams // 2
    teams = range(1, n_teams + 1)
    weeks = range(n_weeks)
    periods = range(n_periods)
    pairs = [(h, a) for h in teams for a in teams if h != a]   # home team, away team

    model = gp.Model("sports_scheduling")

    # game[w, p, h, a] is 1 when team h plays at home against team a in week w, period p.
    # A team never plays itself, so only pairs of different teams get a variable.
    game = model.addVars([(w, p, h, a) for w in weeks for p in periods for (h, a) in pairs],
                         vtype=GRB.BINARY, name="game")

    # Every slot holds exactly one game.
    for w in weeks:
        for p in periods:
            model.addConstr(game.sum(w, p, "*", "*") == 1, name=f"slot[{w},{p}]")

    # Every team plays once a week.
    for w in weeks:
        for t in teams:
            model.addConstr(game.sum(w, "*", t, "*") + game.sum(w, "*", "*", t) == 1, name=f"week[{w},{t}]")

    # Every team plays every other team, at home or away.
    for t1 in teams:
        for t2 in teams:
            if t1 < t2:
                model.addConstr(game.sum("*", "*", t1, t2) + game.sum("*", "*", t2, t1) >= 1,
                                name=f"meet[{t1},{t2}]")

    # Every team plays at most twice in the same period over the tournament.
    for t in teams:
        for p in periods:
            model.addConstr(game.sum("*", p, t, "*") + game.sum("*", p, "*", t) <= 2, name=f"period[{t},{p}]")

    # home[w][p] and away[w][p]: the teams of the game in week w, period p, numbered 1..n.
    home = [[gp.quicksum(h * game[w, p, h, a] for (h, a) in pairs) for p in periods] for w in weeks]
    away = [[gp.quicksum(a * game[w, p, h, a] for (h, a) in pairs) for p in periods] for w in weeks]
    return model, {"home": home, "away": away}
