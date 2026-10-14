# ACC basketball schedule (CSPLib prob011): a double round-robin timetable for the nine teams of the
# 1997/98 Atlantic Coast Conference over 18 dates, with mirroring, home/away/bye pattern, weekend,
# rival and opponent-sequence rules. config[d][t] is the opponent of team t on date d (t itself
# for a bye) and where[d][t] says whether team t plays at home (0), has a bye (1) or is away (2).
from exact import Exact


def build(instance):
    n_teams = instance["n_teams"]
    n_days = instance["n_days"]
    teams = range(n_teams)
    days = range(n_days)

    # The teams and the rules below are those of the ACC problem (9 teams, 18 dates), taken from
    # the problem statement and the reference rather than from the instance.
    CLEM, DUKE, FSU, GT, UMD, UNC, NCSt, UVA, WAKE = range(9)
    HOME, BYE, AWAY = 0, 1, 2
    rivals = [GT, UNC, FSU, CLEM, UVA, DUKE, WAKE, UMD, NCSt]  # rivals[t]; FSU has none
    # Nemhauser and Trick's mirroring scheme: dates (r1, r2) with the same pairings, 0-based.
    mirrored = [(0, 7), (1, 8), (2, 11), (3, 12), (4, 13), (5, 14), (6, 15), (9, 16), (10, 17)]
    weekends = [d for d in days if d % 2 == 1]  # the second and every later even date

    solver = Exact()

    # Variables are 0/1 indicators of the schedule, from which the integer outputs are derived.
    #   meet[d][a][b] (a < b): teams a and b play each other on date d (one variable for both
    #                          directions, so "if i plays j then j plays i" holds by construction)
    #   hosts[d][t][o]       : on date d team t plays team o at home (in t's venue)
    #   bye[d][t], at_home[d][t], away[d][t]: team t has a bye / plays at home / plays away on date d
    def meet_name(d, a, b):
        return f"meet_{d}_{min(a, b)}_{max(a, b)}"

    def hosts_name(d, t, o):
        return f"hosts_{d}_{t}_{o}"

    for d in days:
        for a in teams:
            for b in range(a + 1, n_teams):
                solver.addVariable(meet_name(d, a, b), 0, 1)
            for o in teams:
                if o != a:
                    solver.addVariable(hosts_name(d, a, o), 0, 1)
            for kind in ("bye", "at_home", "away"):
                solver.addVariable(f"{kind}_{d}_{a}", 0, 1)

    def plays(d, t, o):
        """name of the variable that is 1 when team t's opponent on date d is o (o == t: bye)"""
        return f"bye_{d}_{t}" if o == t else meet_name(d, t, o)

    # config[d][t] and where[d][t] are the declared outputs; both are channelled below.
    config = [[f"config_{d}_{t}" for t in teams] for d in days]
    where = [[f"where_{d}_{t}" for t in teams] for d in days]
    for d in days:
        for t in teams:
            solver.addVariable(config[d][t], 0, n_teams - 1)
            solver.addVariable(where[d][t], 0, 2)

    for d in days:
        for t in teams:
            # On each date a team plays exactly one team or has a bye. Because meet is shared by
            # the two teams, the opponents of all teams on a date are different, and if i plays j
            # then j plays i.
            solver.addConstraint([(1, plays(d, t, o)) for o in teams], True, 1, True, 1)

            # When two teams meet, one is at home and the other away: meet = hosts[t][o] + hosts[o][t]
            for o in teams:
                if o > t:
                    solver.addConstraint([(1, meet_name(d, t, o)), (-1, hosts_name(d, t, o)),
                                          (-1, hosts_name(d, o, t))], True, 0, True, 0)
            # A team is at home when it hosts someone, and away when someone hosts it.
            solver.addConstraint([(1, f"at_home_{d}_{t}")] +
                                 [(-1, hosts_name(d, t, o)) for o in teams if o != t],
                                 True, 0, True, 0)
            solver.addConstraint([(1, f"away_{d}_{t}")] +
                                 [(-1, hosts_name(d, o, t)) for o in teams if o != t],
                                 True, 0, True, 0)

            # config[d][t] is the opponent (t itself for a bye); where[d][t] is 0 at home, 1 on a
            # bye, 2 away.
            solver.addConstraint([(1, config[d][t])] + [(-o, plays(d, t, o)) for o in teams if o != 0],
                                 True, 0, True, 0)
            solver.addConstraint([(1, where[d][t]), (-BYE, f"bye_{d}_{t}"), (-AWAY, f"away_{d}_{t}")],
                                 True, 0, True, 0)

    # Double round-robin: each team plays each other team twice, once at home and once away.
    for t in teams:
        for o in teams:
            if o != t:
                solver.addConstraint([(1, hosts_name(d, t, o)) for d in days], True, 1, True, 1)

    # 1. Mirroring: the dates are grouped in pairs (r1, r2) that have the same pairings, with home
    # and away exchanged (where[r1] = 2 - where[r2], so a bye stays a bye).
    for r1, r2 in mirrored:
        for t in teams:
            solver.addConstraint([(1, f"bye_{r1}_{t}"), (-1, f"bye_{r2}_{t}")], True, 0, True, 0)
            for o in teams:
                if o > t:
                    solver.addConstraint([(1, meet_name(r1, t, o)), (-1, meet_name(r2, t, o))],
                                         True, 0, True, 0)
                if o != t:
                    solver.addConstraint([(1, hosts_name(r1, t, o)), (-1, hosts_name(r2, o, t))],
                                         True, 0, True, 0)

    # 2. No two final aways: no team plays away on both of the last two dates.
    for t in teams:
        solver.addConstraint([(1, f"away_{n_days - 2}_{t}"), (1, f"away_{n_days - 1}_{t}")],
                             False, 0, True, 1)

    # 3. Home/away/bye pattern constraints
    for t in teams:
        # No team has more than two home matches in a row, nor more than two away matches in a row.
        for d in range(n_days - 2):
            solver.addConstraint([(1, f"at_home_{k}_{t}") for k in range(d, d + 3)],
                                 False, 0, True, 2)
            solver.addConstraint([(1, f"away_{k}_{t}") for k in range(d, d + 3)],
                                 False, 0, True, 2)
        # No team has more than three away matches or byes in a row.
        for d in range(n_days - 3):
            solver.addConstraint([(1, f"{kind}_{k}_{t}") for k in range(d, d + 4)
                                  for kind in ("away", "bye")], False, 0, True, 3)
        # No team has more than four home matches or byes in a row.
        for d in range(n_days - 4):
            solver.addConstraint([(1, f"{kind}_{k}_{t}") for k in range(d, d + 5)
                                  for kind in ("at_home", "bye")], False, 0, True, 4)

    # 4. Weekend pattern: of the weekends, each team plays four at home, four away and one bye.
    for t in teams:
        for kind, count in (("at_home", 4), ("away", 4), ("bye", 1)):
            solver.addConstraint([(1, f"{kind}_{d}_{t}") for d in weekends], True, count, True, count)

    # 5. First weekends: each team has a home match or a bye on at least two of the first five weekends.
    for t in teams:
        solver.addConstraint([(1, f"{kind}_{d}_{t}") for d in weekends[:5]
                              for kind in ("at_home", "bye")], True, 2)

    # 6. Rival matches: on the last date every team except FSU plays its rival, unless it plays FSU
    # or has a bye. The three cases exclude each other, so their sum must be at least 1.
    last = n_days - 1
    for t in teams:
        if t != FSU:
            solver.addConstraint([(1, plays(last, t, rivals[t])), (1, plays(last, t, FSU)),
                                  (1, plays(last, t, t))], True, 1)

    # 7. Constrained matches: Wake-UNC, Wake-Duke, GT-UNC and GT-Duke are each played at least once
    # in dates 11 to 18 (0-based 10..17).
    for a, b in ((WAKE, UNC), (WAKE, DUKE), (GT, UNC), (GT, DUKE)):
        solver.addConstraint([(1, meet_name(d, a, b)) for d in range(10, n_days)], True, 1)

    # 8. Opponent sequence constraints
    for t in teams:
        # No team plays two dates in a row away against UNC and Duke (in either order).
        if t not in (DUKE, UNC):
            for d in range(n_days - 1):
                for first, second in ((UNC, DUKE), (DUKE, UNC)):
                    solver.addConstraint([(1, meet_name(d, t, first)), (1, f"away_{d}_{t}"),
                                          (1, meet_name(d + 1, t, second)),
                                          (1, f"away_{d + 1}_{t}")], False, 0, True, 3)
        # No team plays three dates in a row against UNC, Duke and Wake in any order
        # (home or away).
        if t not in (UNC, DUKE, WAKE):
            for d in range(n_days - 2):
                for x, y, z in ((UNC, DUKE, WAKE), (UNC, WAKE, DUKE), (DUKE, UNC, WAKE),
                                (DUKE, WAKE, UNC), (WAKE, UNC, DUKE), (WAKE, DUKE, UNC)):
                    solver.addConstraint([(1, meet_name(d, t, x)), (1, meet_name(d + 1, t, y)),
                                          (1, meet_name(d + 2, t, z))], False, 0, True, 2)

    # 9. Other constraints
    # UNC plays its rival Duke on the last date and on date 11.
    solver.addConstraint([(1, meet_name(10, UNC, DUKE))], True, 1, True, 1)
    solver.addConstraint([(1, meet_name(last, UNC, DUKE))], True, 1, True, 1)
    # UNC plays Clem on the second date.
    solver.addConstraint([(1, meet_name(1, UNC, CLEM))], True, 1, True, 1)
    # Duke has a bye on date 16.
    solver.addConstraint([(1, f"bye_15_{DUKE}")], True, 1, True, 1)
    # Wake does not play home on date 17.
    solver.addConstraint([(1, f"at_home_16_{WAKE}")], True, 0, True, 0)
    # Wake has a bye on the first date.
    solver.addConstraint([(1, f"bye_0_{WAKE}")], True, 1, True, 1)
    # Clem, Duke, UMD and Wake do not play away on the last date.
    for t in (CLEM, DUKE, UMD, WAKE):
        solver.addConstraint([(1, f"away_{last}_{t}")], True, 0, True, 0)
    # Clem, FSU, GT and Wake do not play away on the first date.
    for t in (CLEM, FSU, GT, WAKE):
        solver.addConstraint([(1, f"away_0_{t}")], True, 0, True, 0)
    # Neither FSU nor NCSt has a bye on the last date.
    for t in (FSU, NCSt):
        solver.addConstraint([(1, f"bye_{last}_{t}")], True, 0, True, 0)
    # UNC does not have a bye on the first date.
    solver.addConstraint([(1, f"bye_0_{UNC}")], True, 0, True, 0)

    return solver, {"config": config, "where": where}
