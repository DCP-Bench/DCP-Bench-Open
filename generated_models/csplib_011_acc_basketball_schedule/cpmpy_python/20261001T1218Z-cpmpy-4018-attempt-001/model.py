# CSPLib prob011: timetable of the 1997/98 Atlantic Coast Conference basketball season. The 9 teams
# play a double round-robin (each pair meets once at each team's home) over 18 dates, subject to
# the mirroring, home/away/bye pattern, weekend, rival and other constraints of the problem.
import numpy as np
import cpmpy as cp


def build(instance):
    n_teams = instance["n_teams"]
    n_days = instance["n_days"]

    # The team names, the rival pairs and the mirroring scheme below belong to the ACC problem
    # statement itself (they only make sense for 9 teams and 18 dates), so they are mirrored here.
    teams = np.arange(n_teams)
    CLEM, DUKE, FSU, GT, UMD, UNC, NCSt, UVA, WAKE = teams
    # rivals[t] = traditional rival of team t (FSU has none and is paired with itself)
    rivals = [GT, UNC, FSU, CLEM, UVA, DUKE, WAKE, UMD, NCSt]

    days = np.arange(n_days)
    # The first and all odd-numbered dates are weekdays; the 2nd, 4th, ... dates are weekends.
    weekends = np.where(days % 2 == 1)[0]

    # config[d, i] = j: team i plays team j on date d (j == i means team i has a bye on date d)
    config = cp.intvar(0, n_teams - 1, shape=(n_days, n_teams), name="config")
    # where[d, i]: team i plays at home (0), has a bye (1) or plays away (2) on date d
    where = cp.intvar(0, 2, shape=(n_days, n_teams), name="where")
    HOME, BYE, AWAY = 0, 1, 2

    model = cp.Model()

    # A team cannot have different opponents on the same date: no team is paired twice on a date.
    for day_conf in config:
        model += cp.AllDifferent(day_conf)

    # If team i plays team j on a date, then team j plays team i on that date.
    for day in range(n_days):
        for t in range(n_teams):
            model += config[day][config[day, t]] == t

    # Link config and where: when two teams play each other one is at home and the other away,
    # and a team plays itself exactly when it has a bye.
    for day in range(n_days):
        for t in range(n_teams):
            model += (where[day, t] == HOME) == ((config[day, t] != t) & (where[day][config[day, t]] == AWAY))
            model += (where[day, t] == AWAY) == ((config[day, t] != t) & (where[day][config[day, t]] == HOME))
            model += (where[day, t] == BYE) == (config[day, t] == t)

    # Double round-robin: every team meets every other team exactly once at its own home.
    for t in teams:
        for opponent in teams:
            if t != opponent:
                model += cp.sum((config[:, t] == opponent) & (where[:, t] == HOME)) == 1

    # 1. Mirroring: the dates are paired (1,8), (2,9), (3,12), (4,13), (5,14), (6,15), (7,16),
    # (10,17), (11,18). A team plays the same opponent on both dates of a pair, with home and
    # away swapped. scheme[d] = the 0-based date paired with date d.
    scheme = np.array([7, 8, 11, 12, 13, 14, 15, 0, 1, 16, 17, 2, 3, 4, 5, 6, 9, 10])
    model += config == config[scheme]
    model += where == (2 - where[scheme])

    # 2. No team plays away on both of the last two dates.
    for t in range(n_teams):
        model += cp.sum(where[-2:, t] == AWAY) <= 1

    # 3. Home/away/bye patterns, checked over every window of consecutive dates.
    for t in teams:
        for d in days[:-2]:
            # No team has more than two home matches in a row.
            model += cp.sum(where[d:d + 3, t] == HOME) <= 2
            # No team has more than two away matches in a row.
            model += cp.sum(where[d:d + 3, t] == AWAY) <= 2
        for d in days[:-3]:
            # No team has more than three away matches or byes in a row.
            model += cp.sum((where[d:d + 4, t] == AWAY) | (where[d:d + 4, t] == BYE)) <= 3
        for d in days[:-4]:
            # No team has more than four home matches or byes in a row.
            model += cp.sum((where[d:d + 5, t] == HOME) | (where[d:d + 5, t] == BYE)) <= 4

    # 4. Weekend pattern: over the nine weekends each team plays four at home, four away, and
    # has one bye.
    for t in range(n_teams):
        model += cp.sum(where[weekends, t] == HOME) == 4
        model += cp.sum(where[weekends, t] == AWAY) == 4
        model += cp.sum(where[weekends, t] == BYE) == 1

    # 5. First weekends: each team has home matches or byes on at least two of the first five
    # weekends.
    for t in range(n_teams):
        model += (cp.sum(where[weekends[:5], t] == HOME) + cp.sum(where[weekends[:5], t] == BYE)) >= 2

    # 6. Rival matches: on the last date every team except FSU plays its rival, unless it plays
    # FSU or has a bye.
    for t in teams:
        if t != FSU:
            model += (config[-1, t] == rivals[t]) | (config[-1, t] == FSU) | (where[-1, t] == BYE)

    # 7. Constrained matches: Wake-UNC, Wake-Duke, GT-UNC and GT-Duke each occur at least once
    # in dates 11 to 18.
    model += cp.sum(config[10:, WAKE] == UNC) >= 1
    model += cp.sum(config[10:, WAKE] == DUKE) >= 1
    model += cp.sum(config[10:, GT] == UNC) >= 1
    model += cp.sum(config[10:, GT] == DUKE) >= 1

    # 8. Opponent sequences.
    for t in teams:
        for d in days[:-1]:
            if t != DUKE and t != UNC:
                # No team plays away against UNC and Duke on two consecutive dates (either order).
                model += ~((config[d, t] == UNC) & (where[d, t] == AWAY) &
                           (config[d + 1, t] == DUKE) & (where[d + 1, t] == AWAY))
                model += ~((config[d, t] == DUKE) & (where[d, t] == AWAY) &
                           (config[d + 1, t] == UNC) & (where[d + 1, t] == AWAY))
        for d in days[:-2]:
            if t not in [UNC, DUKE, WAKE]:
                # No team plays UNC, Duke and Wake on three consecutive dates (any order, home
                # or away).
                for a, b, c in [(UNC, DUKE, WAKE), (UNC, WAKE, DUKE), (DUKE, UNC, WAKE),
                                (DUKE, WAKE, UNC), (WAKE, UNC, DUKE), (WAKE, DUKE, UNC)]:
                    model += ~((config[d, t] == a) & (config[d + 1, t] == b) & (config[d + 2, t] == c))

    # 9. Other constraints.
    # UNC plays its rival Duke on date 11 and on the last date.
    model += config[10, UNC] == DUKE
    model += config[-1, UNC] == DUKE
    # UNC plays Clem on the second date.
    model += config[1, UNC] == CLEM
    # Duke has a bye on date 16.
    model += where[15, DUKE] == BYE
    # Wake does not play at home on date 17.
    model += where[16, WAKE] != HOME
    # Wake has a bye on the first date.
    model += where[0, WAKE] == BYE
    # Clem, Duke, UMD and Wake do not play away on the last date.
    model += where[-1, [CLEM, DUKE, UMD, WAKE]] != AWAY
    # Clem, FSU, GT and Wake do not play away on the first date.
    model += where[0, [CLEM, FSU, GT, WAKE]] != AWAY
    # Neither FSU nor NCSt has a bye on the last date.
    model += where[-1, [FSU, NCSt]] != BYE
    # UNC does not have a bye on the first date.
    model += where[0, UNC] != BYE

    return model, {"config": config, "where": where}
