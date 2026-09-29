# Sports tournament scheduling: n teams play over n-1 weeks, each week has n/2
# periods, and a period holds one match (a home team and an away team). Every
# team plays once a week, at most twice in the same period over the whole
# tournament, and meets every other team. Teams are numbered 1..n.
from ortools.sat.python import cp_model


def build(instance):
    n_teams = instance["n_teams"]
    n_weeks = n_teams - 1
    n_periods = n_teams // 2
    teams = range(1, n_teams + 1)

    model = cp_model.CpModel()

    # is_home[w][p][t] / is_away[w][p][t] is true when team t is the home / away
    # team of the match in week w, period p (one-hot form of the two schedules)
    is_home = [[{t: model.new_bool_var(f"home_{w}_{p}_{t}") for t in teams} for p in range(n_periods)]
               for w in range(n_weeks)]
    is_away = [[{t: model.new_bool_var(f"away_{w}_{p}_{t}") for t in teams} for p in range(n_periods)]
               for w in range(n_weeks)]
    # home[w][p], away[w][p] = the team number in the slot
    home = [[model.new_int_var(1, n_teams, f"home_{w}_{p}") for p in range(n_periods)] for w in range(n_weeks)]
    away = [[model.new_int_var(1, n_teams, f"away_{w}_{p}") for p in range(n_periods)] for w in range(n_weeks)]

    for w in range(n_weeks):
        for p in range(n_periods):
            # each slot is filled by exactly one team
            model.add_exactly_one(is_home[w][p].values())
            model.add_exactly_one(is_away[w][p].values())
            model.add(home[w][p] == sum(t * is_home[w][p][t] for t in teams))
            model.add(away[w][p] == sum(t * is_away[w][p][t] for t in teams))
            # a team does not play itself
            model.add(home[w][p] != away[w][p])

    # every team plays exactly once a week: the n slots of a week (home and
    # away, all periods) hold n different teams, that is, each team once
    for w in range(n_weeks):
        for t in teams:
            model.add(sum(is_home[w][p][t] + is_away[w][p][t] for p in range(n_periods)) == 1)

    # every team meets every other team at least once, at home or away
    for t1 in teams:
        for t2 in range(t1 + 1, n_teams + 1):
            meetings = []
            for w in range(n_weeks):
                for p in range(n_periods):
                    for a, b in ((t1, t2), (t2, t1)):
                        both = model.new_bool_var(f"meet_{w}_{p}_{a}_{b}")
                        model.add_bool_and([is_home[w][p][a], is_away[w][p][b]]).only_enforce_if(both)
                        model.add_bool_or([is_home[w][p][a].negated(), is_away[w][p][b].negated()]).only_enforce_if(
                            both.negated()
                        )
                        meetings.append(both)
            model.add(sum(meetings) >= 1)

    # a team plays at most twice in the same period over the tournament
    for t in teams:
        for p in range(n_periods):
            model.add(sum(is_home[w][p][t] + is_away[w][p][t] for w in range(n_weeks)) <= 2)

    return model, {"home": home, "away": away}
