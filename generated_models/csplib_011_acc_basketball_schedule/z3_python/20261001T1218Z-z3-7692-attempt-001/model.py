# ACC basketball schedule (CSPLib 11): build a double round-robin timetable for the
# nine 1997/98 Atlantic Coast Conference teams over 18 dates, each team playing
# every other team once at home and once away, under nine groups of side rules.
import z3


def build(instance):
    n_teams = instance["n_teams"]
    n_days = instance["n_days"]
    teams = range(n_teams)
    days = range(n_days)

    # Problem data: the nine ACC teams (their numbering is the reference's).
    CLEM, DUKE, FSU, GT, UMD, UNC, NCSt, UVA, WAKE = range(9)
    # Problem data: each team's traditional rival (FSU has none, so it lists itself).
    rivals = [GT, UNC, FSU, CLEM, UVA, DUKE, WAKE, UMD, NCSt]
    # Problem data: the mirroring scheme of Nemhauser and Trick, as pairs of dates
    # (0-based): dates 1 and 8, 2 and 9, 3 and 12, 4 and 13, 5 and 14, 6 and 15,
    # 7 and 16, 10 and 17, 11 and 18.
    mirror_pairs = [(0, 7), (1, 8), (2, 11), (3, 12), (4, 13), (5, 14), (6, 15),
                    (9, 16), (10, 17)]
    # The first and all odd dates are weekdays, so even-numbered 1-based dates,
    # i.e. odd 0-based indices, are weekend fixtures.
    weekends = [d for d in days if d % 2 == 1]
    last = n_days - 1

    # Boolean encoding. The reference uses integer matrices config[d][t] (the
    # opponent of team t on date d, equal to t itself for a bye) and where[d][t]
    # (home 0, bye 1, away 2); one-hot Booleans give Z3's SAT core and its
    # cardinality constraints something to propagate on, which integer
    # element-style constraints do not.
    #   play[d][t][u]: on date d team t plays team u (u == t means t has a bye)
    #   home[d][t], away[d][t]: on date d team t plays at home / away
    play = [[[z3.Bool(f"play_{d}_{t}_{u}") for u in teams] for t in teams] for d in days]
    home = [[z3.Bool(f"home_{d}_{t}") for t in teams] for d in days]
    away = [[z3.Bool(f"away_{d}_{t}") for t in teams] for d in days]

    def bye(d, t):
        return play[d][t][t]

    solver = z3.Solver()

    for d in days:
        for t in teams:
            # A team has exactly one opponent per date (or a bye), so a team
            # cannot have different opponents on the same date.
            solver.add(z3.PbEq([(play[d][t][u], 1) for u in teams], 1))
            # On each date a team plays at home, plays away, or has a bye.
            solver.add(z3.PbEq([(home[d][t], 1), (away[d][t], 1), (bye(d, t), 1)], 1))
            for u in teams:
                if u > t:
                    # If team t plays team u then team u plays team t.
                    solver.add(play[d][t][u] == play[d][u][t])
                if u != t:
                    # When two teams play each other, one is home and the other away.
                    solver.add(z3.Implies(play[d][t][u], home[d][t] == away[d][u]))
                    solver.add(z3.Implies(play[d][t][u], away[d][t] == home[d][u]))

    # Double round-robin: each team plays each other team exactly once at home
    # (and so once away, by the pairing above).
    for t in teams:
        for opponent in teams:
            if t != opponent:
                solver.add(z3.PbEq(
                    [(z3.And(play[d][t][opponent], home[d][t]), 1) for d in days], 1))

    # 1. Mirroring: the dates in each pair have the same opponents, with home and
    #    away swapped (a bye stays a bye).
    for d1, d2 in mirror_pairs:
        for t in teams:
            for u in teams:
                solver.add(play[d1][t][u] == play[d2][t][u])
            solver.add(home[d1][t] == away[d2][t])
            solver.add(away[d1][t] == home[d2][t])

    for t in teams:
        # 2. No team plays away on both of the last two dates.
        solver.add(z3.AtMost(away[last - 1][t], away[last][t], 1))

        # 3. Home/away/bye patterns.
        for d in days:
            # No team has more than two home matches in a row.
            if d + 3 <= n_days:
                solver.add(z3.AtMost(*[home[k][t] for k in range(d, d + 3)], 2))
                # No team has more than two away matches in a row.
                solver.add(z3.AtMost(*[away[k][t] for k in range(d, d + 3)], 2))
            # No team has more than three away matches or byes in a row.
            if d + 4 <= n_days:
                solver.add(z3.AtMost(
                    *[z3.Or(away[k][t], bye(k, t)) for k in range(d, d + 4)], 3))
            # No team has more than four home matches or byes in a row.
            if d + 5 <= n_days:
                solver.add(z3.AtMost(
                    *[z3.Or(home[k][t], bye(k, t)) for k in range(d, d + 5)], 4))

        # 4. Weekend pattern: of the weekends each team plays four at home, four
        #    away and has one bye.
        solver.add(z3.PbEq([(home[d][t], 1) for d in weekends], 4))
        solver.add(z3.PbEq([(away[d][t], 1) for d in weekends], 4))
        solver.add(z3.PbEq([(bye(d, t), 1) for d in weekends], 1))

        # 5. First weekends: each team has a home match or a bye on at least two
        #    of the first five weekends.
        solver.add(z3.AtLeast(*[z3.Or(home[d][t], bye(d, t)) for d in weekends[:5]], 2))

        # 6. Rival matches: on the last date every team except FSU plays its rival,
        #    unless it plays FSU or has a bye.
        if t != FSU:
            solver.add(z3.Or(play[last][t][rivals[t]], play[last][t][FSU], bye(last, t)))

    # 7. Constrained matches: Wake-UNC, Wake-Duke, GT-UNC and GT-Duke each occur at
    #    least once on dates 11 to 18.
    for team, opponent in [(WAKE, UNC), (WAKE, DUKE), (GT, UNC), (GT, DUKE)]:
        solver.add(z3.Or([play[d][team][opponent] for d in range(10, n_days)]))

    # 8. Opponent sequences.
    for t in teams:
        if t != DUKE and t != UNC:
            for d in range(n_days - 1):
                # No team plays away against UNC and Duke on two consecutive dates.
                for first, second in [(UNC, DUKE), (DUKE, UNC)]:
                    solver.add(z3.Not(z3.And(
                        play[d][t][first], away[d][t],
                        play[d + 1][t][second], away[d + 1][t])))
        if t not in (UNC, DUKE, WAKE):
            for d in range(n_days - 2):
                # No team plays UNC, Duke and Wake on three consecutive dates,
                # in any order and whether home or away.
                for a, b, c in [(UNC, DUKE, WAKE), (UNC, WAKE, DUKE), (DUKE, UNC, WAKE),
                                (DUKE, WAKE, UNC), (WAKE, UNC, DUKE), (WAKE, DUKE, UNC)]:
                    solver.add(z3.Not(z3.And(
                        play[d][t][a], play[d + 1][t][b], play[d + 2][t][c])))

    # 9. Other constraints.
    # UNC plays its rival Duke on the last date and on date 11.
    solver.add(play[10][UNC][DUKE], play[last][UNC][DUKE])
    # UNC plays Clemson on the second date.
    solver.add(play[1][UNC][CLEM])
    # Duke has a bye on date 16.
    solver.add(bye(15, DUKE))
    # Wake does not play at home on date 17.
    solver.add(z3.Not(home[16][WAKE]))
    # Wake has a bye on the first date.
    solver.add(bye(0, WAKE))
    # Clemson, Duke, Maryland and Wake do not play away on the last date.
    for t in (CLEM, DUKE, UMD, WAKE):
        solver.add(z3.Not(away[last][t]))
    # Clemson, Florida State, Georgia Tech and Wake do not play away on the first date.
    for t in (CLEM, FSU, GT, WAKE):
        solver.add(z3.Not(away[0][t]))
    # Neither Florida State nor NC State has a bye on the last date.
    for t in (FSU, NCSt):
        solver.add(z3.Not(bye(last, t)))
    # UNC does not have a bye on the first date.
    solver.add(z3.Not(bye(0, UNC)))

    # Declared outputs, as the reference's integer matrices: config[d][t] is the
    # opponent of team t on date d (t itself for a bye); where[d][t] is 0 for
    # home, 1 for a bye and 2 for away.
    config = [[z3.Sum([z3.If(play[d][t][u], u, 0) for u in teams]) for t in teams]
              for d in days]
    where = [[z3.If(home[d][t], 0, z3.If(away[d][t], 2, 1)) for t in teams]
             for d in days]

    return solver, {"config": config, "where": where}
