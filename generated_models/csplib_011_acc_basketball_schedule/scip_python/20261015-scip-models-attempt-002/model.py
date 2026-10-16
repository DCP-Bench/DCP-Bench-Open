# ACC 1997/98 basketball timetable: a double round-robin of 9 teams over 18 dates, with the
# mirroring, home/away/bye pattern, weekend, rival and opponent-sequence rules of the description.
# Team indices follow the order Clemson, Duke, FSU, GT, UMD, UNC, NCSt, UVA, Wake.
# Dates are numbered from 1 in the description; the code uses 0-based day indices.
from pyscipopt import Model, quicksum

CLEM, DUKE, FSU, GT, UMD, UNC, NCST, UVA, WAKE = range(9)
# rival pairs of the description (FSU has no rival)
RIVAL = {DUKE: UNC, UNC: DUKE, CLEM: GT, GT: CLEM, NCST: WAKE, WAKE: NCST, UMD: UVA, UVA: UMD}
# mirroring scheme of the description, as 1-based date pairs
MIRROR = [(1, 8), (2, 9), (3, 12), (4, 13), (5, 14), (6, 15), (7, 16), (10, 17), (11, 18)]


def build(instance):
    n = instance["n_teams"]
    nd = instance["n_days"]
    T = range(n)
    D = range(nd)
    last = nd - 1

    m = Model()

    # h[d, i, j] = 1 if team i plays at home against team j on day d
    h = {(d, i, j): m.addVar(vtype="B", name=f"home_{d}_{i}_{j}") for d in D for i in T for j in T if i != j}
    # bye[d, i] = 1 if team i has a bye on day d
    bye = {(d, i): m.addVar(vtype="B", name=f"bye_{d}_{i}") for d in D for i in T}

    def meet(d, i, j):
        # 1 if i and j play each other on day d, at either venue
        return h[d, i, j] + h[d, j, i]

    def home(d, i):
        # 1 if team i plays at home on day d
        return quicksum(h[d, i, j] for j in T if j != i)

    def away(d, i):
        # 1 if team i plays away on day d
        return quicksum(h[d, j, i] for j in T if j != i)

    def play(d, i):
        # 1 if team i plays a match on day d
        return quicksum(meet(d, i, j) for j in T if j != i)

    # every team plays one match or has a bye on each day
    # (a team with a bye cannot also play, so no team plays twice on one day)
    for d in D:
        for i in T:
            m.addCons(play(d, i) + bye[d, i] == 1)

    # redundant: 9 teams and 18 dates give 72 matches, at most 4 per date, so every date has
    # exactly 4 matches and one bye; each team has exactly two byes in total
    for d in D:
        m.addCons(quicksum(bye[d, i] for i in T) == 1)
    for i in T:
        m.addCons(quicksum(bye[d, i] for d in D) == 2)

    # double round-robin: each pair plays once at home for each side
    # each team plays each other team once at home and once away
    for i in T:
        for j in T:
            if i != j:
                m.addCons(quicksum(h[d, i, j] for d in D) == 1)

    # mirroring: the two dates of a mirror pair have the same opponents for every team
    # the dates of each pair give every team the same opponent
    for a, b in MIRROR:
        for i in T:
            for j in T:
                if i < j:
                    m.addCons(meet(a - 1, i, j) == meet(b - 1, i, j))

    # no two final aways: no team plays away on both of the last two dates
    # (the last two dates are 17 and 18)
    for i in T:
        m.addCons(away(last - 1, i) + away(last, i) <= 1)

    # home/away/bye pattern: runs of home or away matches and byes
    # no more than two away matches in a row
    # no more than two home matches in a row
    # no more than three away matches or byes in a row
    # no more than four home matches or byes in a row
    for i in T:
        for d in range(nd - 2):
            m.addCons(quicksum(away(d + k, i) for k in range(3)) <= 2)
            m.addCons(quicksum(home(d + k, i) for k in range(3)) <= 2)
        for d in range(nd - 3):
            m.addCons(quicksum(away(d + k, i) + bye[d + k, i] for k in range(4)) <= 3)
        for d in range(nd - 4):
            m.addCons(quicksum(home(d + k, i) + bye[d + k, i] for k in range(5)) <= 4)

    # weekend pattern: the weekends are the even-numbered dates (odd 0-based indices)
    # over the weekends each team plays four at home, four away and has one bye
    weekends = [d for d in D if d % 2 == 1]
    for i in T:
        m.addCons(quicksum(home(d, i) for d in weekends) == 4)
        m.addCons(quicksum(away(d, i) for d in weekends) == 4)
        m.addCons(quicksum(bye[d, i] for d in weekends) == 1)

    # first weekends: each team has home matches or byes on at least two of the first five weekends
    # (weekends are dates 2, 4, 6, 8, 10)
    first_weekends = [1, 3, 5, 7, 9]
    for i in T:
        m.addCons(quicksum(home(d, i) + bye[d, i] for d in first_weekends) >= 2)

    # rival matches: in the last date, every team except FSU plays its rival,
    # unless it plays FSU or has a bye
    for i, r in RIVAL.items():
        m.addCons(meet(last, i, r) + meet(last, i, FSU) + bye[last, i] >= 1)

    # constrained matches: Wake-UNC, Wake-Duke, GT-UNC and GT-Duke occur at least once
    # in dates 11 to 18
    for a, b in [(WAKE, UNC), (WAKE, DUKE), (GT, UNC), (GT, DUKE)]:
        m.addCons(quicksum(meet(d, a, b) for d in range(10, nd)) >= 1)

    # opponent sequence: no team plays away against UNC and Duke on two consecutive dates
    # (teams other than UNC and Duke, since they cannot play themselves)
    for i in T:
        if i in (UNC, DUKE):
            continue
        for d in range(nd - 1):
            m.addCons(h[d, UNC, i] + h[d + 1, DUKE, i] <= 1)
            m.addCons(h[d, DUKE, i] + h[d + 1, UNC, i] <= 1)

    # opponent sequence: no team plays against UNC, Duke and Wake on three consecutive dates,
    # in any order, whether home or away
    trio = [UNC, DUKE, WAKE]
    perms = [(a, b, c) for a in trio for b in trio for c in trio if len({a, b, c}) == 3]
    for i in T:
        if i in trio:
            continue
        for d in range(nd - 2):
            for p, q, r in perms:
                m.addCons(meet(d, i, p) + meet(d + 1, i, q) + meet(d + 2, i, r) <= 2)

    # other constraints of the description (dates converted to 0-based days)
    # UNC plays Duke in the last date and in date 11
    m.addCons(meet(last, UNC, DUKE) == 1)
    m.addCons(meet(10, UNC, DUKE) == 1)
    # UNC plays Clemson in the second date
    m.addCons(meet(1, UNC, CLEM) == 1)
    # Duke has a bye in date 16
    m.addCons(bye[15, DUKE] == 1)
    # Wake does not play at home in date 17
    m.addCons(home(16, WAKE) == 0)
    # Wake has a bye in the first date
    m.addCons(bye[0, WAKE] == 1)
    # Clemson, Duke, UMD and Wake do not play away in the last date
    for i in (CLEM, DUKE, UMD, WAKE):
        m.addCons(away(last, i) == 0)
    # Clemson, FSU, GT and Wake do not play away in the first date
    for i in (CLEM, FSU, GT, WAKE):
        m.addCons(away(0, i) == 0)
    # neither FSU nor NCSt has a bye in the last date
    m.addCons(bye[last, FSU] == 0)
    m.addCons(bye[last, NCST] == 0)
    # UNC does not have a bye in the first date
    m.addCons(bye[0, UNC] == 0)

    # config[d][i] = the team that team i plays on day d; a team with a bye is listed against itself
    config = [
        [
            i * bye[d, i]
            + quicksum(j * h[d, i, j] for j in T if j != i)
            + quicksum(j * h[d, j, i] for j in T if j != i)
            for i in T
        ]
        for d in D
    ]
    # where[d][i] = 0 home, 1 bye, 2 away
    where = [[1 * bye[d, i] + 2 * away(d, i) for i in T] for d in D]

    return m, {"config": config, "where": where}
