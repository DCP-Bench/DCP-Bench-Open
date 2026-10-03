# ACC basketball schedule (CSPLib 11): a double round-robin timetable for the nine teams of
# the 1997/98 Atlantic Coast Conference over 18 dates, with mirroring, home/away/bye
# pattern, weekend, rival and opponent-sequence rules.
import functools
import operator

from hermax.model import Model

# The teams, the rivalries, the mirroring scheme and the special rules are fixed by the
# problem (Nemhauser and Trick); the instance gives the number of teams and dates.
CLEM, DUKE, FSU, GT, UMD, UNC, NCST, UVA, WAKE = range(9)
RIVAL = [GT, UNC, FSU, CLEM, UVA, DUKE, WAKE, UMD, NCST]  # FSU has no rival
# date d is mirrored by date MIRROR[d] (0-based form of the pairs (1, 8), (2, 9), (3, 12),
# (4, 13), (5, 14), (6, 15), (7, 16), (10, 17), (11, 18))
MIRROR = [7, 8, 11, 12, 13, 14, 15, 0, 1, 16, 17, 2, 3, 4, 5, 6, 9, 10]
HOME, BYE, AWAY = 0, 1, 2


def any_of(lits):
    return functools.reduce(operator.or_, lits)


def build(instance):
    n = instance["n_teams"]
    days = instance["n_days"]
    weekends = [d for d in range(days) if d % 2 == 1]  # the second, fourth, ... dates
    last = days - 1

    m = Model()
    # config[d][i] = the team that team i plays on date d; i itself means a bye
    config = m.int_matrix("config", days, n, 0, n - 1)
    # where[d][i] = 0 if team i plays at home on date d, 1 if it has a bye, 2 if it plays away
    where = m.int_matrix("where", days, n, 0, 2)

    # meets[d][i][j] = team i plays team j on date d (meets[d][i][i] = team i has a bye)
    meets = [m.bool_matrix(f"meets_{d}", n, n) for d in range(days)]
    home = m.bool_matrix("home", days, n)
    bye = m.bool_matrix("bye", days, n)
    away = m.bool_matrix("away", days, n)
    for d in range(days):
        for i in range(n):
            for j in range(n):
                m &= (~meets[d][i][j] | (config[d][i] == j))
                m &= (meets[d][i][j] | ~(config[d][i] == j))
            for lit, value in ((home[d][i], HOME), (bye[d][i], BYE), (away[d][i], AWAY)):
                m &= (~lit | (where[d][i] == value))
                m &= (lit | ~(where[d][i] == value))

    for d in range(days):
        # a team cannot have different opponents on the same date, and no two teams have
        # the same opponent
        for j in range(n):
            for i in range(n):
                for k in range(i + 1, n):
                    m &= (~meets[d][i][j] | ~meets[d][k][j])
        for i in range(n):
            # if team i plays team j, then team j plays team i
            for j in range(i + 1, n):
                m &= (~meets[d][i][j] | meets[d][j][i])
                m &= (meets[d][i][j] | ~meets[d][j][i])
            # a team has a bye exactly when it is its own opponent
            m &= (~bye[d][i] | meets[d][i][i])
            m &= (bye[d][i] | ~meets[d][i][i])
            # when two teams play each other, one is at home and the other away
            for j in range(n):
                if j != i:
                    m &= (~meets[d][i][j] | ~home[d][i] | away[d][j])
                    m &= (~meets[d][i][j] | ~away[d][i] | home[d][j])

    # Double round-robin: each team plays each other team exactly once at home.
    for t in range(n):
        for o in range(n):
            if o != t:
                at_home = []
                for d in range(days):
                    lit = m.bool(f"home_game_{t}_{o}_{d}")
                    m &= (~lit | meets[d][t][o])
                    m &= (~lit | home[d][t])
                    m &= (lit | ~meets[d][t][o] | ~home[d][t])
                    at_home.append(lit)
                m &= (sum(at_home) == 1)

    # 1. Mirroring: on mirrored dates every team meets the same opponent, and home and away
    #    swap (a bye stays a bye).
    for d in range(days):
        e = MIRROR[d]
        for i in range(n):
            for j in range(n):
                m &= (~meets[d][i][j] | meets[e][i][j])
            m &= (~home[d][i] | away[e][i])
            m &= (~away[d][i] | home[e][i])
            m &= (~bye[d][i] | bye[e][i])

    for t in range(n):
        # 2. No team plays away on both last dates.
        m &= (~away[last - 1][t] | ~away[last][t])
        # 3. No more than two home matches in a row, no more than two away matches in a row,
        #    no more than three away matches or byes in a row (so one home match in any four
        #    dates), no more than four home matches or byes in a row (so one away match in
        #    any five dates).
        for d in range(days - 2):
            m &= (~home[d][t] | ~home[d + 1][t] | ~home[d + 2][t])
            m &= (~away[d][t] | ~away[d + 1][t] | ~away[d + 2][t])
        for d in range(days - 3):
            m &= any_of([home[d + k][t] for k in range(4)])
        for d in range(days - 4):
            m &= any_of([away[d + k][t] for k in range(5)])
        # 4. Of the weekends, each team plays four at home, four away, and has one bye.
        m &= (sum(home[d][t] for d in weekends) == 4)
        m &= (sum(away[d][t] for d in weekends) == 4)
        m &= (sum(bye[d][t] for d in weekends) == 1)
        # 5. Home matches or byes on at least two of the first five weekends, which is at
        #    most three away matches there.
        m &= (sum(away[d][t] for d in weekends[:5]) <= 3)
        # 6. On the last date every team except FSU plays its rival, unless it plays FSU or
        #    has a bye.
        if t != FSU:
            m &= (meets[last][t][RIVAL[t]] | meets[last][t][FSU] | bye[last][t])

    # 7. These pairings occur at least once in dates 11 to 18: Wake-UNC, Wake-Duke, GT-UNC
    #    and GT-Duke.
    for a, b in ((WAKE, UNC), (WAKE, DUKE), (GT, UNC), (GT, DUKE)):
        m &= any_of([meets[d][a][b] for d in range(10, days)])

    # 8. No team plays away against UNC and Duke on two consecutive dates (in either order),
    #    and no team plays UNC, Duke and Wake on three consecutive dates (in any order).
    for t in range(n):
        if t not in (UNC, DUKE):
            for d in range(days - 1):
                for x, y in ((UNC, DUKE), (DUKE, UNC)):
                    m &= (~meets[d][t][x] | ~away[d][t] | ~meets[d + 1][t][y] | ~away[d + 1][t])
        if t not in (UNC, DUKE, WAKE):
            for d in range(days - 2):
                for x, y, z in ((UNC, DUKE, WAKE), (UNC, WAKE, DUKE), (DUKE, UNC, WAKE),
                                (DUKE, WAKE, UNC), (WAKE, UNC, DUKE), (WAKE, DUKE, UNC)):
                    m &= (~meets[d][t][x] | ~meets[d + 1][t][y] | ~meets[d + 2][t][z])

    # 9. Other constraints.
    # UNC plays its rival Duke in the last date and in date 11
    m &= meets[10][UNC][DUKE]
    m &= meets[last][UNC][DUKE]
    # UNC plays Clem in the second date
    m &= meets[1][UNC][CLEM]
    # Duke has a bye in date 16
    m &= bye[15][DUKE]
    # Wake does not play home in date 17
    m &= ~home[16][WAKE]
    # Wake has a bye in the first date
    m &= bye[0][WAKE]
    # Clem, Duke, UMD and Wake do not play away in the last date
    for t in (CLEM, DUKE, UMD, WAKE):
        m &= ~away[last][t]
    # Clem, FSU, GT and Wake do not play away in the first date
    for t in (CLEM, FSU, GT, WAKE):
        m &= ~away[0][t]
    # Neither FSU nor NCSt have a bye in the last date
    for t in (FSU, NCST):
        m &= ~bye[last][t]
    # UNC does not have a bye in the first date
    m &= ~bye[0][UNC]

    return m, {"config": config, "where": where}
