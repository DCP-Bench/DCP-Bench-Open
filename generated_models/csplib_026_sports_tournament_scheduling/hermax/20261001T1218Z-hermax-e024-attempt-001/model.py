# Sports tournament scheduling: schedule a tournament of n teams over n - 1 weeks, each
# week with n / 2 periods and each period with a home slot and an away slot. Every team
# plays once a week, every team plays every other team, and every team plays at most
# twice in the same period over the tournament. Teams are numbered 1..n.
import functools
import operator

from hermax.model import Model


def at_most_one(m, lits, name):
    """Post "at most one of lits is true" with a ladder encoding.

    prefix[i] says that one of lits[0..i] is true; each literal sets its prefix,
    prefixes carry on, and a literal after a set prefix is forbidden. That takes
    three clauses per literal, where forbidding every pair takes a quadratic number.
    """
    if len(lits) == 1:
        return
    prefix = m.bool_vector(name, len(lits))
    for i, lit in enumerate(lits):
        m &= (~lit | prefix[i])
        if i + 1 < len(lits):
            m &= (~prefix[i] | prefix[i + 1])
            m &= (~lits[i + 1] | ~prefix[i])


def exactly_one(m, lits, name):
    """Post "exactly one of lits is true"."""
    at_most_one(m, lits, name)
    m &= functools.reduce(operator.or_, lits)


def build(instance):
    n_teams = instance["n_teams"]  # number of teams, numbered 1..n_teams
    n_weeks = n_teams - 1
    n_periods = n_teams // 2

    m = Model()
    # is_home[w][p][t - 1] = team t plays at home in period p of week w;
    # is_away[w][p][t - 1] = team t plays away there
    is_home = [[m.bool_vector(f"is_home_{w}_{p}", n_teams) for p in range(n_periods)] for w in range(n_weeks)]
    is_away = [[m.bool_vector(f"is_away_{w}_{p}", n_teams) for p in range(n_periods)] for w in range(n_weeks)]
    # home[w][p], away[w][p] = the home and the away team of period p in week w (the
    # declared outputs), tied to the literals above
    home = [[m.int(f"home_{w}_{p}", 1, n_teams) for p in range(n_periods)] for w in range(n_weeks)]
    away = [[m.int(f"away_{w}_{p}", 1, n_teams) for p in range(n_periods)] for w in range(n_weeks)]

    # every slot has exactly one team
    for w in range(n_weeks):
        for p in range(n_periods):
            exactly_one(m, [is_home[w][p][t] for t in range(n_teams)], f"home_slot_{w}_{p}")
            exactly_one(m, [is_away[w][p][t] for t in range(n_teams)], f"away_slot_{w}_{p}")
    # home and away show the team in the slot: team t means value >= t and not value >= t + 1
    # (comparisons outside the range 1..n_teams are already settled)
    for w in range(n_weeks):
        for p in range(n_periods):
            for slot, var in ((is_home[w][p], home[w][p]), (is_away[w][p], away[w][p])):
                for t in range(1, n_teams + 1):
                    if t > 1:
                        m &= (~slot[t - 1] | (var >= t))
                    if t < n_teams:
                        m &= (~slot[t - 1] | ~(var >= t + 1))

    # a team does not play itself: the home and away teams of a period are different
    for w in range(n_weeks):
        for p in range(n_periods):
            for t in range(n_teams):
                m &= (~is_home[w][p][t] | ~is_away[w][p][t])

    # every team plays once a week: over the home and away slots of a week, each team
    # appears at most once (so the teams of a week are all different; with an even number
    # of teams the slots are as many as the teams, so each team then plays exactly once)
    for w in range(n_weeks):
        for t in range(n_teams):
            appearances = [is_home[w][p][t] for p in range(n_periods)] + [is_away[w][p][t] for p in range(n_periods)]
            at_most_one(m, appearances, f"once_{w}_{t}")

    # every team plays every other team: for each pair of teams there is a period in which
    # one is at home and the other away. met[w][p] only needs to be on when that happens.
    for t1 in range(n_teams):
        for t2 in range(t1 + 1, n_teams):
            meetings = []
            for w in range(n_weeks):
                for p in range(n_periods):
                    for first, second in ((t1, t2), (t2, t1)):
                        met = m.bool()
                        m &= (~met | is_home[w][p][first])
                        m &= (~met | is_away[w][p][second])
                        meetings.append(met)
            m &= functools.reduce(operator.or_, meetings)

    # every team plays at most twice in the same period over the tournament (home or away)
    for t in range(n_teams):
        for p in range(n_periods):
            plays = [is_home[w][p][t] for w in range(n_weeks)] + [is_away[w][p][t] for w in range(n_weeks)]
            m &= (sum(1 * lit for lit in plays) <= 2)

    return m, {"home": home, "away": away}
