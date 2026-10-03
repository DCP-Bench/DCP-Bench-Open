# Sports tournament scheduling (CSPLib 26): schedule n teams over n-1 weeks of n/2 periods, one
# match per period, so that every team plays once a week, at most twice in the same period over
# the tournament, and every team plays every other team.
from pychoco.model import Model


def build(instance):
    n_teams = instance["n_teams"]  # number of teams, numbered 1..n_teams
    n_weeks, n_periods = n_teams - 1, n_teams // 2

    model = Model()

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

    # Every team plays every other team. Each match is mapped to the index of its unordered pair
    # of teams; there are exactly as many slots as pairs (n(n-1)/2), so "every pair meets at least
    # once" is the same as "the pair indices are all different".
    pairs = [(t1, t2) for t1 in range(1, n_teams + 1) for t2 in range(t1 + 1, n_teams + 1)]
    match_pair = []
    for idx, (t1, t2) in enumerate(pairs):
        match_pair += [(t1, t2, idx), (t2, t1, idx)]
    pair_of = []
    for w in range(n_weeks):
        for p in range(n_periods):
            pv = model.intvar(0, len(pairs) - 1, name=f"pair_{w}_{p}")
            model.table([home[w][p], away[w][p], pv], match_pair).post()
            pair_of.append(pv)
    model.all_different(pair_of).post()

    # Every team plays at most twice in the same period over the tournament.
    # Implied lower bound: a team plays all n-1 weeks spread over n/2 periods, at most twice in
    # each, which leaves room for only one missing appearance, so it plays every period at least
    # once. The domain 1..2 states both bounds.
    teams = list(range(1, n_teams + 1))
    for p in range(n_periods):
        in_period = [home[w][p] for w in range(n_weeks)] + [away[w][p] for w in range(n_weeks)]
        occurrences = [model.intvar(1, 2, name=f"plays_{p}_{t}") for t in teams]
        model.global_cardinality(in_period, teams, occurrences).post()

    # Implied opponent view, to help the search: opp[w][t-1] is the team that t meets in week w.
    # Since t meets each other team exactly once over the n-1 weeks, its opponents are all
    # different. Within a week, slot s of home[w] + away[w] is partnered with slot
    # (s + n/2) mod n; slot[w][t-1] is the slot team t occupies.
    partner = [(s, (s + n_periods) % n_teams) for s in range(n_teams)]
    opp = [[model.intvar(1, n_teams, name=f"opp_{w}_{t}") for t in teams] for w in range(n_weeks)]
    for w in range(n_weeks):
        week_slots = home[w] + away[w]
        slot = [model.intvar(0, n_teams - 1, name=f"slot_{w}_{t}") for t in teams]
        # week_slots[s] = t  <=>  slot[t - 1] = s
        model.inverse_channeling(week_slots, slot, 1, 0).post()
        for t in teams:
            other = model.intvar(0, n_teams - 1, name=f"other_{w}_{t}")
            model.table([slot[t - 1], other], partner).post()
            model.element(opp[w][t - 1], week_slots, other).post()
            model.arithm(opp[w][t - 1], "!=", t).post()
    for t in teams:
        model.all_different([opp[w][t - 1] for w in range(n_weeks)]).post()

    return model, {"home": home, "away": away}
