#!/usr/bin/python3
# Category: csplib
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/csplib/prob011_basketball_schedule.py
# Source description: https://www.csplib.org/Problems/prob011/

"""
The problem is finding a timetable for the 1997/98 Atlantic Coast Conference (ACC) in basketball.

The 9 basketball teams in the tournament are Clemson (Clem), Duke (Duke), Florida State (FSU), Georgia Tech (GT),
Maryland (UMD), North Carolina (UNC), North Carolina State (NCSt), Virginia (UVA), and Wake Forest (Wake). The
problem is to determine a double round-robin schedule for these 9 teams subject to some additional constraints. In a
double round-robin, each team plays each other, once at home, once away. The schedule is to be played over 18 dates.
The first and all subsequent odd dates are weekday fixtures. The second and all subsequent even dates are weekend
fixtures. There are nine other sets of constraints.

1. Mirroring. The dates are grouped into pairs (r1, r2), such that each team will get to play against the same team
in dates r1 and r2. Such a grouping is called a mirroring scheme. Nemhauser and Trick use the mirroring scheme {(1,
8), (2, 9), (3, 12), (4, 13), (5, 14), (6, 15), (7, 16), (10, 17), (11, 18)}

2. No Two Final Aways. No team can play away on both last dates.

3. Home/Away/Bye Pattern Constraints. No team may have more than two away matches in a row. No team may have more
than two home matches in a row. No team may have more than three away matches or byes in a row. No team may have more
than four home matches or byes in a row.

4. Weekend Pattern. Of the weekends, each team plays four at home, four away, and one bye.

5. First Weekends. Each team must have home matches or byes at least on two of the first five weekends.

6. Rival Matches. Every team except FSU has a traditional rival. The rival pairs are Duke-UNC, Clem-GT, NCSt-Wake,
and UMD-UVA. In the last date, every team except FSU plays against its rival, unless it plays against FSU or has a bye.

7. Constrained Matches. The following pairings must occur at least once in dates 11 to 18: Wake-UNC, Wake-Duke,
GT-UNC, and GT-Duke.

8. Opponent Sequence Constraints. No team plays in two consecutive dates away against UNC and Duke. No team plays in
three consecutive dates against UNC, Duke and Wake (independent of home/away).

9. Other Constraints. UNC plays its rival Duke in the last date, and in date 11. UNC plays Clem in the second date.
Duke has a bye in date 16. Wake does not play home in date 17. Wake has a bye in the first date. Clem, Duke,
UMD and Wake do not play away in the last date. Clem, FSU, GT and Wake do not play away in the first date. Neither
FSU nor NCSt have a bye in the last date. UNC does not have a bye in the first date.

Print the match configuration (config) as a list of lists, where each inner list represents a day and contains the
teams playing on that day; config[d,i] == j means that team i plays against team j on day d. Also print whether each
team is playing home -0-, away -2-, or has a bye -1- (where); e.g. where[d,i] == 0 means that team i plays at home on day d.
"""

# Data
n_teams = 9
n_days = 18
# End of data

# Import libraries
from cpmpy import *
import numpy as np
import json


def basketball_schedule():
    n_teams = 9
    n_days = 18

    # Teams
    teams = np.arange(n_teams)
    CLEM, DUKE, FSU, GT, UMD, UNC, NCSt, UVA, WAKE = teams
    rivals = [GT, UNC, FSU, CLEM, UVA, DUKE, WAKE, UMD, NCSt]

    # Days
    days = np.arange(n_days)
    weekends = np.where(days % 2 == 1)[0]

    # matrix indicating which teams play against each other at what date
    # config[d,i] == j iff team i plays team j on day d of the tournament, if i == j then team i has a bye on day d of the tournament
    config = intvar(0, n_teams - 1, shape=(n_days, n_teams), name="config")
    where = intvar(0, 2, shape=(n_days, n_teams), name="where")
    HOME, BYE, AWAY = 0, 1, 2

    model = Model()

    # a team cannot have different opponents on the same day
    for day_conf in config:
        model += AllDifferent(day_conf)

    # if team i plays team j, then team j plays team i
    for day in range(n_days):
        for t in range(n_teams):
            model += config[day, config[day, t]] == t

    # connect config and where (when two teams play each other, one is home, the other away)
    for day in range(n_days):
        for t in range(n_teams):
            model += (where[day, t] == HOME) == ((config[day, t] != t) & (where[day, config[day, t]] == AWAY))
            model += (where[day, t] == AWAY) == ((config[day, t] != t) & (where[day, config[day, t]] == HOME))
            model += (where[day, t] == BYE) == (config[day, t] == t)

    # Double round-robin: each team plays each other team twice (once home and once away)
    model += all([sum((config[:, t] == opponent) & (where[:, t] == HOME)) == 1
                  for t in teams for opponent in teams if t != opponent])

    # 1. mirroring constraint
    scheme = np.array([7, 8, 11, 12, 13, 14, 15, 0, 1, 16, 17, 2, 3, 4, 5, 6, 9, 10])
    model += config == config[scheme]
    model += where == (2 - where[scheme])

    # 2. no two final days away
    for t in range(n_teams):
        model += sum(where[-2:, t] == AWAY) <= 1

    # 3. home/away/bye pattern constraint
    for t in teams:
        for d in days[:-3]:
            # No team may have more than two home matches in a row
            model += sum(where[d:d + 3, t] == HOME) <= 2
            # No team may have more than two away matches in a row
            model += sum(where[d:d + 3, t] == AWAY) <= 2

        for d in days[:-4]:
            # No team may have more than three away matches or byes in a row
            model += sum((where[d:d + 4, t] == AWAY) | (where[d:d + 4, t] == BYE)) <= 3

        for d in days[:-5]:
            # No team may have more than four home matches or byes in a row.
            model += sum((where[d:d + 5, t] == HOME) | (where[d:d + 5, t] == BYE)) <= 4

    # 4. weekend pattern constraint
    # Of the weekends, each team plays four at home, four away, and one bye.
    for t in range(n_teams):
        model += sum(where[weekends, t] == HOME) == 4
        model += sum(where[weekends, t] == AWAY) == 4
        model += sum(where[weekends, t] == BYE) == 1

    # 5. first weekends constraint
    # Each team must have home matches or byes at least on two of the first five weekends.
    for t in range(n_teams):
        model += (sum(where[weekends[:5], t] == HOME) + sum(where[weekends[:5], t] == BYE)) >= 2

    # 6. rival matches constraint
    # In the last date, every team except FSU plays against its rival, unless it plays against FSU or has a bye.
    for t in teams:
        if t != FSU:
            model += (config[-1, t] == rivals[t]) | (config[-1, t] == FSU) | (where[-1, t] == BYE)

    # 7. Constrained matches
    # The following pairings must occur at least once in dates 11 to 18:
    # Wake-UNC, Wake-Duke, GT-UNC, and GT-Duke.
    model += sum(config[10:, WAKE] == UNC) >= 1
    model += sum(config[10:, WAKE] == DUKE) >= 1
    model += sum(config[10:, GT] == UNC) >= 1
    model += sum(config[10:, GT] == DUKE) >= 1

    # 8. Opponent Sequence constraints
    for t in teams:
        for d in days[:-1]:
            if t != DUKE and t != UNC:
                # No team plays in two consecutive dates away against UNC and Duke
                model += ~((config[d, t] == UNC) & (where[d, t] == AWAY) &
                          (config[d + 1, t] == DUKE) & (where[d + 1, t] == AWAY))
                model += ~((config[d, t] == DUKE) & (where[d, t] == AWAY) &
                          (config[d + 1, t] == UNC) & (where[d + 1, t] == AWAY))
        for d in days[:-2]:
            if t not in [UNC, DUKE, WAKE]:
                # No team plays in three consecutive dates against UNC, Duke and Wake (independent of home/away).
                model += ~((config[d, t] == UNC) & (config[d + 1, t] == DUKE) & (config[d + 2, t] == WAKE))
                model += ~((config[d, t] == UNC) & (config[d + 1, t] == WAKE) & (config[d + 2, t] == DUKE))
                model += ~((config[d, t] == DUKE) & (config[d + 1, t] == UNC) & (config[d + 2, t] == WAKE))
                model += ~((config[d, t] == DUKE) & (config[d + 1, t] == WAKE) & (config[d + 2, t] == UNC))
                model += ~((config[d, t] == WAKE) & (config[d + 1, t] == UNC) & (config[d + 2, t] == DUKE))
                model += ~((config[d, t] == WAKE) & (config[d + 1, t] == DUKE) & (config[d + 2, t] == UNC))

    # 9. Other constraints
    # UNC plays its rival Duke in the last date and in date 11
    model += config[10, UNC] == DUKE
    model += config[-1, UNC] == DUKE
    # UNC plays Clem in the second date
    model += config[1, UNC] == CLEM
    # Duke has a bye in date 16
    model += where[15, DUKE] == BYE
    # Wake does not play home in date 17
    model += where[16, WAKE] != HOME
    # Wake has a bye in the first date
    model += where[0, WAKE] == BYE
    # Clem, Duke, UMD and Wake do not play away in the last date
    model += where[-1, [CLEM, DUKE, UMD, WAKE]] != AWAY
    # Clem, FSU, GT and Wake do not play away in the first date
    model += where[0, [CLEM, FSU, GT, WAKE]] != AWAY
    # Neither FSU nor NCSt have a bye in last date
    model += where[-1, [FSU, NCSt]] != BYE
    # UNC does not have a bye in the first date.
    model += where[0, UNC] != BYE

    return model, (config, where)


# Example usage
model, (config, where) = basketball_schedule()

# Solve
model.solve()

# Print
solution = {
    "config": config.value().tolist(),
    "where": where.value().tolist()
}
print(json.dumps(solution))
# End of CPMPy script
