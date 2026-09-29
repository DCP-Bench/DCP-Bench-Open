# ACC basketball schedule: a double round-robin for nine teams over 18 dates
# (odd dates are weekdays, even dates weekends), where every team meets every
# other team once at home and once away, with the mirroring, home/away pattern,
# rival and special-request rules of the 1997/98 Atlantic Coast Conference.
# config[d][t] is the opponent of team t on date d (t itself for a bye) and
# where[d][t] is 0 for home, 1 for a bye and 2 for away.
from itertools import permutations

from ortools.sat.python import cp_model

HOME, BYE, AWAY = 0, 1, 2

# The teams and the league's requests are fixed by the problem, so they are mirrored here.
CLEM, DUKE, FSU, GT, UMD, UNC, NCST, UVA, WAKE = range(9)
RIVALS = [GT, UNC, FSU, CLEM, UVA, DUKE, WAKE, UMD, NCST]  # traditional rival of each team (FSU has none)
# mirroring scheme: date d has the same pairings as date MIRROR[d] (0-based dates)
MIRROR = [7, 8, 11, 12, 13, 14, 15, 0, 1, 16, 17, 2, 3, 4, 5, 6, 9, 10]


def build(instance):
    n_teams = instance["n_teams"]
    n_days = instance["n_days"]
    teams = range(n_teams)
    days = range(n_days)
    weekends = [d for d in days if d % 2 == 1]  # the second, fourth, ... dates
    last = n_days - 1

    model = cp_model.CpModel()

    # plays[d][t][u] is true when team t meets team u on date d (u == t means a bye)
    plays = [[[model.new_bool_var(f"plays_{d}_{t}_{u}") for u in teams] for t in teams] for d in days]
    # home[d][t], bye[d][t], away[d][t]: what team t does on date d
    home = [[model.new_bool_var(f"home_{d}_{t}") for t in teams] for d in days]
    away = [[model.new_bool_var(f"away_{d}_{t}") for t in teams] for d in days]
    bye = [[plays[d][t][t] for t in teams] for d in days]  # a bye is playing oneself

    config = [[model.new_int_var(0, n_teams - 1, f"config_{d}_{t}") for t in teams] for d in days]
    where = [[model.new_int_var(0, 2, f"where_{d}_{t}") for t in teams] for d in days]

    for d in days:
        for t in teams:
            # a team has exactly one opponent per date, and config reports its number
            model.add_exactly_one(plays[d][t])
            model.add(config[d][t] == sum(u * plays[d][t][u] for u in teams))
            # a team is at home, away or has a bye, and where reports which
            model.add_exactly_one([home[d][t], bye[d][t], away[d][t]])
            model.add(where[d][t] == HOME * home[d][t] + BYE * bye[d][t] + AWAY * away[d][t])
            for u in teams:
                # if team t plays team u then team u plays team t, which also
                # means no two teams share an opponent on the same date
                model.add(plays[d][t][u] == plays[d][u][t])
                # when two teams meet, one is at home and the other away
                if u != t:
                    model.add(home[d][t] == away[d][u]).only_enforce_if(plays[d][t][u])
                    model.add(away[d][t] == home[d][u]).only_enforce_if(plays[d][t][u])

    # double round-robin: each team plays every other team exactly once at home
    for t in teams:
        for u in teams:
            if u != t:
                at_home = []
                for d in days:
                    both = model.new_bool_var(f"home_game_{d}_{t}_{u}")
                    model.add_bool_and([plays[d][t][u], home[d][t]]).only_enforce_if(both)
                    model.add_bool_or([plays[d][t][u].negated(), home[d][t].negated()]).only_enforce_if(both.negated())
                    at_home.append(both)
                model.add(sum(at_home) == 1)

    # 1. mirroring: dates d and MIRROR[d] have the same pairings with home and away swapped
    for d in days:
        m = MIRROR[d]
        for t in teams:
            for u in teams:
                model.add(plays[d][t][u] == plays[m][t][u])
            model.add(home[d][t] == away[m][t])
            model.add(away[d][t] == home[m][t])

    # 2. no team plays away on both of the last two dates
    for t in teams:
        model.add(away[last - 1][t] + away[last][t] <= 1)

    # 3. home/away/bye pattern limits on runs of consecutive dates
    for t in teams:
        for d in range(n_days - 2):
            # at most two home matches in a row
            model.add(sum(home[e][t] for e in range(d, d + 3)) <= 2)
            # at most two away matches in a row
            model.add(sum(away[e][t] for e in range(d, d + 3)) <= 2)
        for d in range(n_days - 3):
            # at most three away matches or byes in a row
            model.add(sum(away[e][t] + bye[e][t] for e in range(d, d + 4)) <= 3)
        for d in range(n_days - 4):
            # at most four home matches or byes in a row
            model.add(sum(home[e][t] + bye[e][t] for e in range(d, d + 5)) <= 4)

    # 4. weekend pattern: on the weekends each team is four times home, four times away, once on a bye
    for t in teams:
        model.add(sum(home[d][t] for d in weekends) == 4)
        model.add(sum(away[d][t] for d in weekends) == 4)
        model.add(sum(bye[d][t] for d in weekends) == 1)

    # 5. first weekends: home matches or byes on at least two of the first five weekends
    for t in teams:
        model.add(sum(home[d][t] + bye[d][t] for d in weekends[:5]) >= 2)

    # 6. rival matches: on the last date every team but FSU plays its rival, unless it plays FSU or has a bye
    for t in teams:
        if t != FSU:
            model.add_bool_or([plays[last][t][RIVALS[t]], plays[last][t][FSU], bye[last][t]])

    # 7. constrained matches: these pairings occur at least once on dates 11 to 18
    for a, b in [(WAKE, UNC), (WAKE, DUKE), (GT, UNC), (GT, DUKE)]:
        model.add(sum(plays[d][a][b] for d in range(10, n_days)) >= 1)

    # 8. opponent sequences
    for t in teams:
        for d in range(n_days - 1):
            if t not in (DUKE, UNC):
                # no team plays away against UNC and Duke on two consecutive dates (either order)
                for a, b in [(UNC, DUKE), (DUKE, UNC)]:
                    model.add_bool_or([plays[d][t][a].negated(), away[d][t].negated(),
                                       plays[d + 1][t][b].negated(), away[d + 1][t].negated()])
        for d in range(n_days - 2):
            if t not in (UNC, DUKE, WAKE):
                # no team plays UNC, Duke and Wake on three consecutive dates, in any order
                for a, b, c in permutations([UNC, DUKE, WAKE]):
                    model.add_bool_or([plays[d][t][a].negated(), plays[d + 1][t][b].negated(),
                                       plays[d + 2][t][c].negated()])

    # 9. other requests
    model.add(plays[10][UNC][DUKE] == 1)  # UNC plays Duke on date 11 ...
    model.add(plays[last][UNC][DUKE] == 1)  # ... and on the last date
    model.add(plays[1][UNC][CLEM] == 1)  # UNC plays Clemson on the second date
    model.add(bye[15][DUKE] == 1)  # Duke has a bye on date 16
    model.add(home[16][WAKE] == 0)  # Wake does not play at home on date 17
    model.add(bye[0][WAKE] == 1)  # Wake has a bye on the first date
    for t in (CLEM, DUKE, UMD, WAKE):
        model.add(away[last][t] == 0)  # these teams do not play away on the last date
    for t in (CLEM, FSU, GT, WAKE):
        model.add(away[0][t] == 0)  # these teams do not play away on the first date
    for t in (FSU, NCST):
        model.add(bye[last][t] == 0)  # no bye on the last date for FSU and NC State
    model.add(bye[0][UNC] == 0)  # UNC has no bye on the first date

    return model, {"config": config, "where": where}
