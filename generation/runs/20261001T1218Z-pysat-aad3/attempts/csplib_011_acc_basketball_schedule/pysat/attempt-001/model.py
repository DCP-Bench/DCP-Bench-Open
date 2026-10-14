# ACC basketball schedule (CSPLib 11): a double round-robin timetable for 9 basketball teams
# over 18 dates (odd dates are weekday fixtures, even dates weekend fixtures), where each team
# plays every other team once at home and once away, subject to nine groups of side constraints.
# config[d][i] = j says that team i plays team j on date d (j = i is a bye), where[d][i] says
# whether team i plays at home (0), has a bye (1) or plays away (2).
from itertools import permutations

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    n_teams = instance["n_teams"]
    n_days = instance["n_days"]

    # The teams, their rivals and the other data below belong to the problem statement.
    CLEM, DUKE, FSU, GT, UMD, UNC, NCSt, UVA, WAKE = range(9)
    assert n_teams == 9 and n_days == 18, "the constraints below are written for the ACC problem"
    rival_pairs = [(DUKE, UNC), (CLEM, GT), (NCSt, WAKE), (UMD, UVA)]  # FSU has no rival
    rival = {}
    for first, second in rival_pairs:
        rival[first], rival[second] = second, first
    # Mirroring scheme: pairs of dates (1-based in the statement) in which each team plays the
    # same opponent, once at home and once away.
    mirror_pairs = [(1, 8), (2, 9), (3, 12), (4, 13), (5, 14), (6, 15), (7, 16), (10, 17), (11, 18)]
    HOME, BYE, AWAY = 0, 1, 2
    days = range(n_days)
    teams = range(n_teams)
    weekends = [d for d in days if d % 2 == 1]  # the even dates of the statement (0-based: odd)
    last = n_days - 1

    pool = IDPool()
    # config[d][t] = the opponent of team t on day d (t itself means a bye)
    config = [[Integer(f"config{d}_{t}", 0, n_teams - 1, vpool=pool) for t in teams] for d in days]
    # where[d][t] = 0 if team t plays at home on day d, 1 if it has a bye, 2 if it plays away
    where = [[Integer(f"where{d}_{t}", 0, 2, vpool=pool) for t in teams] for d in days]
    engine = IntegerEngine(vars=[v for row in config + where for v in row], vpool=pool)

    # a team cannot have different opponents on the same day: all opponents of a day differ
    for d in days:
        engine.add_alldifferent(config[d])

    cnf = engine.clausify()

    def plays(d, t, u):
        return config[d][t].equals(u)

    def home(d, t):
        return where[d][t].equals(HOME)

    def bye(d, t):
        return where[d][t].equals(BYE)

    def away(d, t):
        return where[d][t].equals(AWAY)

    # if team t plays team u on a day, then team u plays team t
    for d in days:
        for t in teams:
            for u in teams:
                cnf.append([-plays(d, t, u), plays(d, u, t)])

    # connect config and where: when two teams play each other, one is at home and the other
    # away; a team plays itself exactly when it has a bye
    for d in days:
        for t in teams:
            cnf.append([-plays(d, t, t), bye(d, t)])
            cnf.append([plays(d, t, t), -bye(d, t)])
            for u in teams:
                if u != t:
                    cnf.append([-plays(d, t, u), -home(d, t), away(d, u)])
                    cnf.append([-plays(d, t, u), home(d, t), -away(d, u)])
                    cnf.append([-plays(d, t, u), -away(d, t), home(d, u)])
                    cnf.append([-plays(d, t, u), away(d, t), -home(d, u)])

    # double round-robin: each team plays each other team exactly once at home (so, with the
    # mirroring below, once away as well)
    for t in teams:
        for u in teams:
            if u != t:
                at_home_against_u = []
                for d in days:
                    literal = pool.id(("home_against", d, t, u))
                    cnf.append([-literal, plays(d, t, u)])
                    cnf.append([-literal, home(d, t)])
                    cnf.append([literal, -plays(d, t, u), -home(d, t)])
                    at_home_against_u.append(literal)
                cnf.extend(CardEnc.equals(lits=at_home_against_u, bound=1, vpool=pool,
                                          encoding=EncType.seqcounter).clauses)

    # 1. Mirroring: on the two dates of a pair every team plays the same opponent, home on one
    # date and away on the other (a bye stays a bye).
    for first, second in mirror_pairs:
        d1, d2 = first - 1, second - 1
        for t in teams:
            for u in teams:
                cnf.append([-plays(d1, t, u), plays(d2, t, u)])
                cnf.append([plays(d1, t, u), -plays(d2, t, u)])
            cnf.append([-home(d1, t), away(d2, t)])
            cnf.append([home(d1, t), -away(d2, t)])
            cnf.append([-away(d1, t), home(d2, t)])
            cnf.append([away(d1, t), -home(d2, t)])
            cnf.append([-bye(d1, t), bye(d2, t)])
            cnf.append([bye(d1, t), -bye(d2, t)])

    for t in teams:
        # 2. No two final aways: no team plays away on both of the last two dates.
        cnf.append([-away(last - 1, t), -away(last, t)])

        # 3. Home/away/bye pattern.
        for d in range(n_days - 2):
            # no more than two home matches in a row
            cnf.append([-home(d, t), -home(d + 1, t), -home(d + 2, t)])
            # no more than two away matches in a row
            cnf.append([-away(d, t), -away(d + 1, t), -away(d + 2, t)])
        for d in range(n_days - 3):
            # no more than three away matches or byes in a row: one of four dates is at home
            cnf.append([home(d + k, t) for k in range(4)])
        for d in range(n_days - 4):
            # no more than four home matches or byes in a row: one of five dates is away
            cnf.append([away(d + k, t) for k in range(5)])

        # 4. Weekend pattern: of the weekends, four at home, four away and one bye.
        cnf.extend(CardEnc.equals(lits=[home(d, t) for d in weekends], bound=4, vpool=pool,
                                  encoding=EncType.seqcounter).clauses)
        cnf.extend(CardEnc.equals(lits=[away(d, t) for d in weekends], bound=4, vpool=pool,
                                  encoding=EncType.seqcounter).clauses)
        cnf.extend(CardEnc.equals(lits=[bye(d, t) for d in weekends], bound=1, vpool=pool,
                                  encoding=EncType.seqcounter).clauses)

        # 5. First weekends: home matches or byes (i.e. not away) on at least two of the first
        # five weekends.
        cnf.extend(CardEnc.atleast(lits=[-away(d, t) for d in weekends[:5]], bound=2, vpool=pool,
                                   encoding=EncType.seqcounter).clauses)

        # 6. Rival matches: in the last date every team except FSU plays its rival, unless it
        # plays FSU or has a bye.
        if t != FSU:
            cnf.append([plays(last, t, rival[t]), plays(last, t, FSU), bye(last, t)])

    # 7. Constrained matches: Wake-UNC, Wake-Duke, GT-UNC and GT-Duke are each played at least
    # once in dates 11 to 18.
    for t, u in [(WAKE, UNC), (WAKE, DUKE), (GT, UNC), (GT, DUKE)]:
        cnf.append([plays(d, t, u) for d in range(10, n_days)])

    # 8. Opponent sequences
    for t in teams:
        if t not in (DUKE, UNC):
            # no team plays away against UNC and Duke on two consecutive dates
            for d in range(n_days - 1):
                for first, second in [(UNC, DUKE), (DUKE, UNC)]:
                    cnf.append([-plays(d, t, first), -away(d, t),
                                -plays(d + 1, t, second), -away(d + 1, t)])
        if t not in (UNC, DUKE, WAKE):
            # no team plays UNC, Duke and Wake on three consecutive dates (in any order, home or away)
            for d in range(n_days - 2):
                for order in permutations([UNC, DUKE, WAKE]):
                    cnf.append([-plays(d + k, t, order[k]) for k in range(3)])

    # 9. Other constraints
    cnf.append([plays(10, UNC, DUKE)])      # UNC plays Duke in date 11 ...
    cnf.append([plays(last, UNC, DUKE)])    # ... and in the last date
    cnf.append([plays(1, UNC, CLEM)])       # UNC plays Clem in the second date
    cnf.append([bye(15, DUKE)])             # Duke has a bye in date 16
    cnf.append([-home(16, WAKE)])           # Wake does not play home in date 17
    cnf.append([bye(0, WAKE)])              # Wake has a bye in the first date
    for t in (CLEM, DUKE, UMD, WAKE):
        cnf.append([-away(last, t)])        # Clem, Duke, UMD and Wake do not play away in the last date
    for t in (CLEM, FSU, GT, WAKE):
        cnf.append([-away(0, t)])           # Clem, FSU, GT and Wake do not play away in the first date
    for t in (FSU, NCSt):
        cnf.append([-bye(last, t)])         # neither FSU nor NCSt has a bye in the last date
    cnf.append([-bye(0, UNC)])              # UNC does not have a bye in the first date

    return cnf, {"config": config, "where": where}
