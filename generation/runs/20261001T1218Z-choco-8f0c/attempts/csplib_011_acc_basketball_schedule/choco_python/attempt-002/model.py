# ACC basketball scheduling (CSPLib 11): a double round-robin timetable for the nine teams of the
# 1997/98 Atlantic Coast Conference over 18 dates, under the conference's mirroring, home/away/bye
# pattern, weekend, rival and opponent-sequence rules.
from pychoco.model import Model

# Team names, rivals, the mirroring scheme and the fixed-date rules are part of the problem
# statement, not of the instance; they are written for 9 teams and 18 dates.
CLEM, DUKE, FSU, GT, UMD, UNC, NCST, UVA, WAKE = range(9)
RIVALS = [GT, UNC, FSU, CLEM, UVA, DUKE, WAKE, UMD, NCST]  # FSU has no rival
# Nemhauser and Trick's mirroring scheme {(1,8), (2,9), (3,12), (4,13), (5,14), (6,15), (7,16),
# (10,17), (11,18)}, as 0-based "date d mirrors date MIRROR[d]".
MIRROR = [7, 8, 11, 12, 13, 14, 15, 0, 1, 16, 17, 2, 3, 4, 5, 6, 9, 10]
HOME, BYE, AWAY = 0, 1, 2


def build(instance):
    n_teams = instance["n_teams"]
    n_days = instance["n_days"]
    teams = range(n_teams)
    days = range(n_days)
    weekends = [d for d in days if d % 2 == 1]  # the second and every other date

    model = Model()

    # config[d][i] = j: team i plays team j on date d; config[d][i] = i is a bye
    config = [[model.intvar(0, n_teams - 1, name=f"config_{d}_{i}") for i in teams] for d in days]
    # where[d][i] = 0 home, 1 bye, 2 away
    where = [[model.intvar(0, 2, name=f"where_{d}_{i}") for i in teams] for d in days]

    # Booleans for the home/bye/away status, used by the counting rules below.
    is_home = [[model.arithm(where[d][i], "=", HOME).reify() for i in teams] for d in days]
    is_bye = [[model.arithm(where[d][i], "=", BYE).reify() for i in teams] for d in days]
    is_away = [[model.arithm(where[d][i], "=", AWAY).reify() for i in teams] for d in days]
    fixed = [model.intvar(t, t, name=f"team_{t}") for t in teams]

    for d in days:
        # A team cannot have different opponents on the same date.
        model.all_different(config[d]).post()
        for t in teams:
            # If team t plays team j, then team j plays team t.
            model.element(fixed[t], config[d], config[d][t]).post()
            # A bye is exactly a match against oneself.
            model.arithm(config[d][t], "=", t).reify_with(is_bye[d][t])
            # When two teams meet, one is home and the other away: the statuses of t and its
            # opponent add up to 2 (a bye pairs t with itself, 1 + 1).
            opp_where = model.intvar(0, 2, name=f"opp_where_{d}_{t}")
            model.element(opp_where, where[d], config[d][t]).post()
            model.arithm(where[d][t], "+", opp_where, "=", 2).post()

    # Double round-robin: each team hosts every other team exactly once. Each date of team t is
    # coded as opponent + n * status, so the code is o for a home match against o. Implied by the
    # rule and the pairing above: each team also visits every other team once, and with 2(n-1)
    # matches over n_days dates it has n_days - 2(n-1) byes.
    for t in teams:
        code = []
        for d in days:
            c = model.intvar(0, 3 * n_teams - 1, name=f"code_{d}_{t}")
            model.scalar([config[d][t], where[d][t]], [1, n_teams], "=", c).post()
            code.append(c)
        values, occurrences = [], []
        for o in teams:
            if o != t:
                values += [o + n_teams * HOME, o + n_teams * AWAY]
                occurrences += [model.intvar(1, 1), model.intvar(1, 1)]
        n_byes = n_days - 2 * (n_teams - 1)
        values.append(t + n_teams * BYE)
        occurrences.append(model.intvar(n_byes, n_byes))
        model.global_cardinality(code, values, occurrences, closed=True).post()

    # Implied counts, which every schedule satisfies and which help the solver prune:
    # each team meets every other team on two dates and has n_days - 2(n-1) byes, and so plays
    # n-1 home and n-1 away matches; on every date the n teams (an odd number) form (n-1)/2
    # matches, so exactly one team has a bye (one at least, and 2 byes per team over n_days
    # dates leave room for no more).
    for t in teams:
        counts = [model.intvar(2, 2) if o != t else model.intvar(n_byes, n_byes) for o in teams]
        model.global_cardinality([config[d][t] for d in days], list(teams), counts).post()
        model.sum([is_home[d][t] for d in days], "=", n_teams - 1).post()
        model.sum([is_away[d][t] for d in days], "=", n_teams - 1).post()
        model.sum([is_bye[d][t] for d in days], "=", n_byes).post()
    for d in days:
        model.sum([is_bye[d][t] for t in teams], "=", 1).post()
        model.sum([is_home[d][t] for t in teams], "=", n_teams // 2).post()
        model.sum([is_away[d][t] for t in teams], "=", n_teams // 2).post()

    # 1. Mirroring: paired dates have the same opponents with home and away swapped.
    for d in days:
        for t in teams:
            model.arithm(config[d][t], "=", config[MIRROR[d]][t]).post()
            model.arithm(where[d][t], "+", where[MIRROR[d]][t], "=", 2).post()

    # 2. No team plays away on both last dates.
    for t in teams:
        model.sum([is_away[n_days - 2][t], is_away[n_days - 1][t]], "<=", 1).post()

    # 3. Home/away/bye patterns.
    for t in teams:
        for d in range(n_days - 2):
            # No team has more than two home matches in a row.
            model.sum([is_home[d + k][t] for k in range(3)], "<=", 2).post()
            # No team has more than two away matches in a row.
            model.sum([is_away[d + k][t] for k in range(3)], "<=", 2).post()
        for d in range(n_days - 3):
            # No team has more than three away matches or byes in a row: some date of four is home.
            model.sum([is_home[d + k][t] for k in range(4)], ">=", 1).post()
        for d in range(n_days - 4):
            # No team has more than four home matches or byes in a row: some date of five is away.
            model.sum([is_away[d + k][t] for k in range(5)], ">=", 1).post()

    # 4. Weekend pattern: of the weekends, each team plays four at home, four away and has one bye.
    for t in teams:
        model.sum([is_home[d][t] for d in weekends], "=", 4).post()
        model.sum([is_away[d][t] for d in weekends], "=", 4).post()
        model.sum([is_bye[d][t] for d in weekends], "=", 1).post()

    # 5. First weekends: each team is home or has a bye on at least two of the first five weekends.
    for t in teams:
        model.sum([is_home[d][t] for d in weekends[:5]] + [is_bye[d][t] for d in weekends[:5]],
                  ">=", 2).post()

    # 6. Rival matches: on the last date every team except FSU plays its rival, plays FSU, or has
    # a bye.
    for t in teams:
        if t != FSU:
            model.member(config[n_days - 1][t], sorted({RIVALS[t], FSU, t})).post()

    # 7. Constrained matches: Wake-UNC, Wake-Duke, GT-UNC and GT-Duke each occur at least once in
    # dates 11 to 18.
    for a, b in ((WAKE, UNC), (WAKE, DUKE), (GT, UNC), (GT, DUKE)):
        meetings = model.intvar(1, n_days - 10, name=f"meet_{a}_{b}")
        model.count(b, [config[d][a] for d in range(10, n_days)], meetings).post()

    # 8. Opponent sequences.
    plays = {o: [[model.arithm(config[d][t], "=", o).reify() for t in teams] for d in days]
             for o in (UNC, DUKE, WAKE)}
    for t in teams:
        if t not in (DUKE, UNC):
            # No team plays away against UNC and then away against Duke on consecutive dates, or
            # the other way round.
            for first, second in ((UNC, DUKE), (DUKE, UNC)):
                for d in range(n_days - 1):
                    model.sum([plays[first][d][t], is_away[d][t],
                               plays[second][d + 1][t], is_away[d + 1][t]], "<=", 3).post()
        if t not in (UNC, DUKE, WAKE):
            # No team plays UNC, Duke and Wake on three consecutive dates, in any order.
            orders = [(UNC, DUKE, WAKE), (UNC, WAKE, DUKE), (DUKE, UNC, WAKE),
                      (DUKE, WAKE, UNC), (WAKE, UNC, DUKE), (WAKE, DUKE, UNC)]
            for order in orders:
                for d in range(n_days - 2):
                    model.sum([plays[order[k]][d + k][t] for k in range(3)], "<=", 2).post()

    # 9. Other constraints.
    last = n_days - 1
    # UNC plays its rival Duke on the last date and on date 11.
    model.arithm(config[10][UNC], "=", DUKE).post()
    model.arithm(config[last][UNC], "=", DUKE).post()
    # UNC plays Clem on the second date.
    model.arithm(config[1][UNC], "=", CLEM).post()
    # Duke has a bye on date 16.
    model.arithm(where[15][DUKE], "=", BYE).post()
    # Wake does not play home on date 17.
    model.arithm(where[16][WAKE], "!=", HOME).post()
    # Wake has a bye on the first date.
    model.arithm(where[0][WAKE], "=", BYE).post()
    # Clem, Duke, UMD and Wake do not play away on the last date.
    for t in (CLEM, DUKE, UMD, WAKE):
        model.arithm(where[last][t], "!=", AWAY).post()
    # Clem, FSU, GT and Wake do not play away on the first date.
    for t in (CLEM, FSU, GT, WAKE):
        model.arithm(where[0][t], "!=", AWAY).post()
    # Neither FSU nor NCSt has a bye on the last date.
    for t in (FSU, NCST):
        model.arithm(where[last][t], "!=", BYE).post()
    # UNC does not have a bye on the first date.
    model.arithm(where[0][UNC], "!=", BYE).post()

    return model, {"config": config, "where": where}
