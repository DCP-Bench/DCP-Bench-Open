"""ACC basketball schedule (CSPLib 11): a double round-robin timetable for the nine teams of
the 1997/98 Atlantic Coast Conference over 18 dates (odd dates weekdays, even dates
weekends), with mirroring, home/away/bye pattern, weekend, rival, constrained-match,
opponent-sequence and team-specific rules.

The model reports config[d][i], the opponent of team i on day d (i itself for a bye), and
where[d][i]: 0 home, 1 bye, 2 away.
"""
from itertools import product

import pulp


def build(instance):
    n_teams = instance["n_teams"]
    n_days = instance["n_days"]
    teams = range(n_teams)
    days = range(n_days)

    # The team names, rivals and mirroring scheme belong to the problem statement and are
    # mirrored from the reference.
    CLEM, DUKE, FSU, GT, UMD, UNC, NCSt, UVA, WAKE = range(9)
    rivals = [GT, UNC, FSU, CLEM, UVA, DUKE, WAKE, UMD, NCSt]
    scheme = [7, 8, 11, 12, 13, 14, 15, 0, 1, 16, 17, 2, 3, 4, 5, 6, 9, 10]
    weekends = [d for d in days if d % 2 == 1]
    HOME, BYE, AWAY = 0, 1, 2
    last = n_days - 1

    problem = pulp.LpProblem("acc_basketball_schedule", pulp.LpMinimize)  # satisfaction

    # 1. Mirroring: dates d and scheme[d] have the same pairings with home and away
    # swapped. So only one date of each mirrored pair (the earlier, a "base" date) gets
    # variables, and its partner date is read from it.
    base = [d for d in days if d < scheme[d]]

    # host_var[d][i][j] = 1 if team i plays team j at home on base date d;
    # bye_var[d][i] = 1 if team i does not play on base date d
    host_var = {d: [[pulp.LpVariable(f"host_{d}_{i}_{j}", cat="Binary") if i != j else None
                     for j in teams] for i in teams] for d in base}
    bye_var = {d: [pulp.LpVariable(f"bye_{d}_{i}", cat="Binary") for i in teams] for d in base}

    def host(d, i, j):
        """1 if team i hosts team j on day d; on a mirrored date, j hosts i on its base."""
        return host_var[d][i][j] if d in host_var else host_var[scheme[d]][j][i]

    def bye(d, i):
        return bye_var[d][i] if d in bye_var else bye_var[scheme[d]][i]

    def plays(d, i, j):
        """1 if teams i and j meet on day d (whoever is at home); for i == j, a bye."""
        if i == j:
            return bye(d, i)
        return host(d, i, j) + host(d, j, i)

    def home(d, i):
        return pulp.lpSum(host(d, i, j) for j in teams if j != i)

    def away(d, i):
        return pulp.lpSum(host(d, j, i) for j in teams if j != i)

    # a team has one opponent (or a bye) each day; meetings are mutual by construction,
    # so no two teams share an opponent on the same day
    for d in base:
        for i in teams:
            problem += home(d, i) + away(d, i) + bye(d, i) == 1

    # double round-robin: each team plays each other team once at home (and so once away)
    for i in teams:
        for j in teams:
            if i != j:
                problem += pulp.lpSum(host(d, i, j) for d in days) == 1

    # Rules 2 to 5 only concern one team's home/bye/away sequence. Every sequence that
    # obeys them (and the mirroring) is listed, and each team follows one of them; this
    # is far tighter for the solver than stating the rules on the match variables.
    def allowed(pattern):
        def count(window, kinds):
            return sum(1 for w in window if w in kinds)
        # 2. no team plays away on both last dates
        if count(pattern[-2:], (AWAY,)) > 1:
            return False
        for d in range(n_days - 2):
            # 3. no more than two home matches, or two away matches, in a row
            if count(pattern[d:d + 3], (HOME,)) > 2 or count(pattern[d:d + 3], (AWAY,)) > 2:
                return False
        for d in range(n_days - 3):
            # 3. no more than three away matches or byes in a row
            if count(pattern[d:d + 4], (AWAY, BYE)) > 3:
                return False
        for d in range(n_days - 4):
            # 3. no more than four home matches or byes in a row
            if count(pattern[d:d + 5], (HOME, BYE)) > 4:
                return False
        # 4. of the weekends, four at home, four away and one bye
        on_weekends = [pattern[d] for d in weekends]
        if (on_weekends.count(HOME), on_weekends.count(AWAY), on_weekends.count(BYE)) != (4, 4, 1):
            return False
        # 5. home matches or byes on at least two of the first five weekends
        if count([pattern[d] for d in weekends[:5]], (HOME, BYE)) < 2:
            return False
        return True

    patterns = []
    for choice in product((HOME, BYE, AWAY), repeat=len(base)):
        pattern = [None] * n_days
        for d, w in zip(base, choice):
            pattern[d] = w
            pattern[scheme[d]] = 2 - w  # mirrored date: home and away swap, a bye stays
        if allowed(pattern):
            patterns.append(pattern)

    # follows[i][p] = 1 if team i plays to pattern p; its home and bye days then match it
    follows = [[pulp.LpVariable(f"follows_{i}_{p}", cat="Binary") for p in range(len(patterns))]
               for i in teams]
    def pattern_says(d, i, kind):
        """1 if the pattern team i follows has `kind` on day d"""
        return pulp.lpSum(var for p, var in enumerate(follows[i]) if patterns[p][d] == kind)

    for i in teams:
        problem += pulp.lpSum(follows[i]) == 1
        for d in base:
            problem += home(d, i) == pattern_says(d, i, HOME)
            problem += bye(d, i) == pattern_says(d, i, BYE)
            # the same link stated per match, which the solver's relaxation cannot derive
            # from the sums: i can only host j on a day i is at home and j away
            for j in teams:
                if j != i:
                    problem += host(d, i, j) <= pattern_says(d, i, HOME)
                    problem += host(d, i, j) <= pattern_says(d, j, AWAY)

    # Implied constraints that tighten the relaxation without removing any schedule:
    # two teams on the same pattern would be at home together or away together on every
    # date they play, so they could never meet; every pattern is used at most once.
    for p in range(len(patterns)):
        problem += pulp.lpSum(follows[i][p] for i in teams) <= 1
    # with an odd number of teams, each date has exactly one bye and the other teams split
    # evenly into home and away
    for d in base:
        problem += pulp.lpSum(pattern_says(d, i, BYE) for i in teams) == 1
        problem += pulp.lpSum(pattern_says(d, i, HOME) for i in teams) == (n_teams - 1) // 2

    # 6. On the last date every team except FSU plays its rival, unless it plays FSU or
    #    has a bye: every other opponent is ruled out
    for i in teams:
        if i != FSU:
            for j in teams:
                if j not in (rivals[i], FSU, i):
                    problem += plays(last, i, j) == 0

    # 7. Wake-UNC, Wake-Duke, GT-UNC and GT-Duke each meet at least once in dates 11 to 18
    for a, b in ((WAKE, UNC), (WAKE, DUKE), (GT, UNC), (GT, DUKE)):
        problem += pulp.lpSum(plays(d, a, b) for d in range(10, n_days)) >= 1

    # 8. Opponent sequences
    for t in teams:
        if t not in (DUKE, UNC):
            # no team plays away against UNC and then away against Duke on consecutive
            # dates, or the other way round
            for d in range(n_days - 1):
                problem += host(d, UNC, t) + host(d + 1, DUKE, t) <= 1
                problem += host(d, DUKE, t) + host(d + 1, UNC, t) <= 1
        if t not in (UNC, DUKE, WAKE):
            # no team plays UNC, Duke and Wake on three consecutive dates, in any order
            orders = [(UNC, DUKE, WAKE), (UNC, WAKE, DUKE), (DUKE, UNC, WAKE),
                      (DUKE, WAKE, UNC), (WAKE, UNC, DUKE), (WAKE, DUKE, UNC)]
            for d in range(n_days - 2):
                for a, b, c in orders:
                    problem += plays(d, t, a) + plays(d + 1, t, b) + plays(d + 2, t, c) <= 2

    # 9. Other constraints
    problem += plays(10, UNC, DUKE) == 1     # UNC plays its rival Duke in date 11
    problem += plays(last, UNC, DUKE) == 1   # and in the last date
    problem += plays(1, UNC, CLEM) == 1      # UNC plays Clem in the second date
    problem += bye(15, DUKE) == 1            # Duke has a bye in date 16
    problem += home(16, WAKE) == 0           # Wake does not play home in date 17
    problem += bye(0, WAKE) == 1             # Wake has a bye in the first date
    for t in (CLEM, DUKE, UMD, WAKE):        # these do not play away in the last date
        problem += away(last, t) == 0
    for t in (CLEM, FSU, GT, WAKE):          # these do not play away in the first date
        problem += away(0, t) == 0
    for t in (FSU, NCSt):                    # neither has a bye in the last date
        problem += bye(last, t) == 0
    problem += bye(0, UNC) == 0              # UNC does not have a bye in the first date

    # the opponent of each team each day, and whether it is home (0), bye (1) or away (2)
    config = [[pulp.lpSum(j * plays(d, i, j) for j in teams) for i in teams] for d in days]
    where = [[HOME * home(d, i) + BYE * bye(d, i) + AWAY * away(d, i) for i in teams]
             for d in days]
    return problem, {"config": config, "where": where}
