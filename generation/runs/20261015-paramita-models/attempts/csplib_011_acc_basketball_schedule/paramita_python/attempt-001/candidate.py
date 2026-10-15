# ACC 1997/98 basketball timetable: a double round-robin over 9 teams and 18 dates
# with mirroring, pattern, weekend, rival and opponent-sequence constraints.
from paramita.modelling import Bool, Or

# Team indices, in the order the description lists the teams (problem constants).
CLEM, DUKE, FSU, GT, UMD, UNC, NCST, UVA, WAKE = range(9)
# Traditional rivals (problem constants): Duke-UNC, Clem-GT, NCSt-Wake, UMD-UVA.
RIVAL = {DUKE: UNC, UNC: DUKE, CLEM: GT, GT: CLEM, NCST: WAKE, WAKE: NCST, UMD: UVA, UVA: UMD}
# Mirroring scheme of Nemhauser and Trick (problem constant).
MIRROR = [(1, 8), (2, 9), (3, 12), (4, 13), (5, 14), (6, 15), (7, 16), (10, 17), (11, 18)]


def build(instance):
    n, D = instance["n_teams"], instance["n_days"]
    teams = range(n)
    dates = range(1, D + 1)
    weekends = [d for d in dates if d % 2 == 0]
    first_weekends = [d for d in weekends if d <= 10]
    last = D
    before_last = D - 1

    # home[d,i,j]: team i plays at home against team j on date d.
    home = {(d, i, j): Bool(f"home_{d}_{i}_{j}") for d in dates for i in teams for j in teams if i != j}
    # bye[d,i]: team i does not play on date d.
    bye = {(d, i): Bool(f"bye_{d}_{i}") for d in dates for i in teams}

    def H(d, i):
        # team i plays at home on date d
        return sum(home[d, i, j] for j in teams if j != i)

    def A(d, i):
        # team i plays away on date d
        return sum(home[d, j, i] for j in teams if j != i)

    def M(d, i, j):
        # team i and team j meet on date d, at either venue
        return home[d, i, j] | home[d, j, i]

    cons = []

    # each team plays at most one match a date; otherwise it has a bye
    for d in dates:
        for i in teams:
            cons.append(H(d, i) + A(d, i) + bye[d, i] == 1)

    # double round robin: each team plays each other team once at home
    for i in teams:
        for j in teams:
            if i != j:
                cons.append(sum(home[d, i, j] for d in dates) == 1)

    # mirroring: the same opponent on both dates of each mirror pair
    for r1, r2 in MIRROR:
        for i in teams:
            for j in teams:
                if i != j:
                    cons.append(M(r1, i, j) == M(r2, i, j))

    # no team can play away on both last dates
    for i in teams:
        cons.append(A(before_last, i) + A(last, i) <= 1)

    # no more than two away matches in a row
    for i in teams:
        for d in range(1, D - 1):
            cons.append(sum(A(d + k, i) for k in range(3)) <= 2)

    # no more than two home matches in a row
    for i in teams:
        for d in range(1, D - 1):
            cons.append(sum(H(d + k, i) for k in range(3)) <= 2)

    # no more than three away matches or byes in a row
    for i in teams:
        for d in range(1, D - 2):
            cons.append(sum(A(d + k, i) + bye[d + k, i] for k in range(4)) <= 3)

    # no more than four home matches or byes in a row
    for i in teams:
        for d in range(1, D - 3):
            cons.append(sum(H(d + k, i) + bye[d + k, i] for k in range(5)) <= 4)

    # weekend pattern: over the weekends, four home, four away and one bye
    for i in teams:
        cons.append(sum(H(d, i) for d in weekends) == 4)
        cons.append(sum(A(d, i) for d in weekends) == 4)
        cons.append(sum(bye[d, i] for d in weekends) == 1)

    # first weekends: home matches or byes on at least two of the first five weekends
    for i in teams:
        cons.append(sum(H(d, i) + bye[d, i] for d in first_weekends[:5]) >= 2)

    # rival matches on the last date: every team except FSU meets its rival,
    # unless it meets FSU or has a bye
    for i in teams:
        if i in RIVAL:
            cons.append(Or([M(last, i, RIVAL[i]), M(last, i, FSU), bye[last, i]]))

    # constrained matches: Wake-UNC, Wake-Duke, GT-UNC, GT-Duke occur on dates 11 to 18
    for i, j in [(WAKE, UNC), (WAKE, DUKE), (GT, UNC), (GT, DUKE)]:
        cons.append(Or([M(d, i, j) for d in dates if d >= 11]))

    # opponent sequence: no team plays away at UNC and at Duke on two consecutive dates
    for i in teams:
        for d in range(1, D):
            for x, y in [(UNC, DUKE), (DUKE, UNC)]:
                if i not in (x, y):
                    cons.append(~(home[d, x, i] & home[d + 1, y, i]))

    # opponent sequence: no team plays UNC, Duke and Wake on three consecutive dates
    trio = [UNC, DUKE, WAKE]
    perms = [(a, b, c) for a in trio for b in trio for c in trio if len({a, b, c}) == 3]
    for i in teams:
        if i in trio:
            continue
        for d in range(1, D - 1):
            for a, b, c in perms:
                cons.append(~(M(d, i, a) & M(d + 1, i, b) & M(d + 2, i, c)))

    # UNC plays its rival Duke on the last date and on date 11
    cons.append(M(last, UNC, DUKE))
    cons.append(M(11, UNC, DUKE))
    # UNC plays Clemson on the second date
    cons.append(M(2, UNC, CLEM))
    # Duke has a bye on date 16
    cons.append(bye[16, DUKE])
    # Wake does not play at home on date 17
    cons.append(H(17, WAKE) == 0)
    # Wake has a bye on the first date
    cons.append(bye[1, WAKE])
    # Clemson, Duke, UMD and Wake do not play away on the last date
    for i in [CLEM, DUKE, UMD, WAKE]:
        cons.append(A(last, i) == 0)
    # Clemson, FSU, GT and Wake do not play away on the first date
    for i in [CLEM, FSU, GT, WAKE]:
        cons.append(A(1, i) == 0)
    # neither FSU nor NCSt has a bye on the last date
    cons.append(~bye[last, FSU])
    cons.append(~bye[last, NCST])
    # UNC does not have a bye on the first date
    cons.append(~bye[1, UNC])

    # config[d][i]: the opponent of team i on date d (0-based team index);
    # on a bye the team's own index stands in for the opponent
    config = [
        [
            sum(j * home[d, i, j] + j * home[d, j, i] for j in teams if j != i) + i * bye[d, i]
            for i in teams
        ]
        for d in dates
    ]
    # where[d][i]: 0 home, 1 bye, 2 away
    where = [
        [sum(2 * home[d, j, i] for j in teams if j != i) + 1 * bye[d, i] for i in teams]
        for d in dates
    ]
    return cons, {"config": config, "where": where}
