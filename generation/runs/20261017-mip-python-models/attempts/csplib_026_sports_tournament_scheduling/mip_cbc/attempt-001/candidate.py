# CSPLib 026 sports tournament scheduling: n teams (n even) play a round robin over n-1 weeks.
# Each week has n/2 periods, and each period has two slots: the first team plays at home,
# the second plays the first team away. Output home[w][p] and away[w][p] (1-based teams).
import mip


def build(instance):
    n = instance["n_teams"]
    weeks = n - 1
    periods = n // 2
    teams = range(n)
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # match[w, p, i, j] = 1 when team i plays at home and team j away in week w, period p.
    match = {}
    for w in range(weeks):
        for p in range(periods):
            for i in teams:
                for j in teams:
                    if i != j:
                        match[w, p, i, j] = model.add_var(f"match_{w}_{p}_{i}_{j}", var_type=mip.BINARY)

    # Each period of each week holds exactly one match.
    for w in range(weeks):
        for p in range(periods):
            # one match per period
            model += mip.xsum(match[w, p, i, j] for i in teams for j in teams if i != j) == 1

    # Home and away indicator for team t in (w, p), written as linear sums of match variables.
    def at_home(w, p, t):
        return mip.xsum(match[w, p, t, j] for j in teams if j != t)

    def at_away(w, p, t):
        return mip.xsum(match[w, p, i, t] for i in teams if i != t)

    # Every team plays once a week.
    for w in range(weeks):
        for t in teams:
            # every team plays once a week
            model += mip.xsum(at_home(w, p, t) + at_away(w, p, t) for p in range(periods)) == 1

    # Every team plays at most twice in the same period over the tournament.
    for p in range(periods):
        for t in teams:
            # every team plays at most twice in the same period over the tournament
            model += mip.xsum(at_home(w, p, t) + at_away(w, p, t) for w in range(weeks)) <= 2

    # Every team plays every other team.
    for i in teams:
        for j in teams:
            if i < j:
                # every team plays every other team
                model += (
                    mip.xsum(match[w, p, i, j] + match[w, p, j, i] for w in range(weeks) for p in range(periods))
                    == 1
                )

    # Declared outputs: home[w][p] and away[w][p] as integer teams numbered 1..n.
    home = [[None] * periods for _ in range(weeks)]
    away = [[None] * periods for _ in range(weeks)]
    for w in range(weeks):
        for p in range(periods):
            home[w][p] = model.add_var(f"home_{w}_{p}", lb=1, ub=n, var_type=mip.INTEGER)
            away[w][p] = model.add_var(f"away_{w}_{p}", lb=1, ub=n, var_type=mip.INTEGER)
            # the home and away team numbers of the period
            model += home[w][p] == mip.xsum((t + 1) * at_home(w, p, t) for t in teams)
            model += away[w][p] == mip.xsum((t + 1) * at_away(w, p, t) for t in teams)

    return model, {"home": home, "away": away}
