# Sports tournament scheduling (CSPLib 26): schedule n teams over n-1 weeks of n/2 periods, one
# match per period, so that every team plays once a week, at most twice in the same period over
# the tournament, and every team plays every other team.
from pychoco.model import Model


def build(instance):
    n_teams = instance["n_teams"]  # number of teams, numbered 1..n_teams
    n_weeks, n_periods = n_teams - 1, n_teams // 2
    teams = list(range(1, n_teams + 1))

    model = Model()

    # pair[w][p] = the index of the unordered pair of teams meeting in week w, period p. Declared
    # before home and away; the declaration order was chosen for search speed only.
    pairs = [(t1, t2) for t1 in range(1, n_teams + 1) for t2 in range(t1 + 1, n_teams + 1)]
    pair = [[model.intvar(0, len(pairs) - 1, name=f"pair_{w}_{p}") for p in range(n_periods)]
            for w in range(n_weeks)]

    # home[w][p] / away[w][p] = the team playing at home / away in week w, period p
    home = [[model.intvar(1, n_teams, name=f"home_{w}_{p}") for p in range(n_periods)]
            for w in range(n_weeks)]
    away = [[model.intvar(1, n_teams, name=f"away_{w}_{p}") for p in range(n_periods)]
            for w in range(n_weeks)]

    # A team cannot play itself.
    for w in range(n_weeks):
        for p in range(n_periods):
            model.arithm(home[w][p], "!=", away[w][p]).post()

    # Every team plays once a week.
    for w in range(n_weeks):
        model.all_different(home[w] + away[w]).post()

    # Every team plays every other team. Each match is tied to the index of its unordered pair
    # of teams; there are exactly as many slots as pairs (n(n-1)/2), so "every pair meets at least
    # once" is the same as "the pair indices are all different".
    match_pair = []
    for idx, (t1, t2) in enumerate(pairs):
        match_pair += [(t1, t2, idx), (t2, t1, idx)]
    for w in range(n_weeks):
        for p in range(n_periods):
            model.table([home[w][p], away[w][p], pair[w][p]], match_pair).post()
    model.all_different([pv for row in pair for pv in row]).post()

    # Every team plays at most twice in the same period over the tournament.
    # Stated through an auxiliary "dummy week" (the classical reformulation of this problem): a
    # team plays n-1 weeks over n/2 periods, at most twice in each, so it misses its second
    # appearance in exactly one period. Placing every team once in the dummy week, in the period it
    # appears only once, makes each team appear exactly twice in every period over the real weeks
    # plus the dummy week. Any schedule meeting the rule has such a dummy week and every schedule
    # with one meets the rule, so the declared outputs are unchanged.
    dummy = [model.intvar(1, n_teams, name=f"dummy_{s}") for s in range(n_teams)]
    model.all_different(dummy).post()
    for p in range(n_periods):
        # The two dummy slots of a period hold an unordered pair; ordering them removes the
        # duplicate dummy weeks only, not any schedule.
        model.arithm(dummy[2 * p], "<", dummy[2 * p + 1]).post()
        in_period = ([home[w][p] for w in range(n_weeks)] + [away[w][p] for w in range(n_weeks)]
                     + [dummy[2 * p], dummy[2 * p + 1]])
        twice = [model.intvar(2, 2) for _ in teams]
        model.global_cardinality(in_period, teams, twice).post()

    return model, {"home": home, "away": away}
