"""ACC basketball scheduling: a mirrored double round-robin for 9 teams over 18 dates with the 1997/98 ACC pattern, rival and sequence rules."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    n_teams = instance["n_teams"]
    n_days = instance["n_days"]
    teams = range(n_teams)
    days = range(n_days)
    HOME, BYE, AWAY = 0, 1, 2

    # Team names, rivals, the mirroring scheme and every rule below are the problem's
    # own (the 1997/98 ACC season), mirrored from the reference.
    CLEM, DUKE, FSU, GT, UMD, UNC, NCST, UVA, WAKE = range(9)
    rivals = [GT, UNC, FSU, CLEM, UVA, DUKE, WAKE, UMD, NCST]
    scheme = [7, 8, 11, 12, 13, 14, 15, 0, 1, 16, 17, 2, 3, 4, 5, 6, 9, 10]
    weekends = [d for d in days if d % 2 == 1]

    model = gp.Model("acc_basketball")

    # 1. Mirroring: date d and date scheme[d] have the same pairings with home and away
    # swapped. Only the first date of each mirrored pair gets variables; the other
    # date reads them with the roles exchanged.
    base = [d for d in days if d < scheme[d]]
    game = {(d, i, j): model.addVar(vtype=GRB.BINARY, name=f"game[{d},{i},{j}]")
            for d in base for i in teams for j in teams if i != j}

    def hosts(d, i, j):
        """1 when team i plays at home against team j on date d."""
        return game[d, i, j] if d in base else game[scheme[d], j, i]

    home = [[gp.quicksum(hosts(d, i, j) for j in teams if j != i) for i in teams] for d in days]
    away = [[gp.quicksum(hosts(d, j, i) for j in teams if j != i) for i in teams] for d in days]
    bye = [[1 - home[d][i] - away[d][i] for i in teams] for d in days]

    def meets(d, i, j):
        """1 when teams i and j play each other on date d."""
        return hosts(d, i, j) + hosts(d, j, i)

    # A team plays at most one game a date (otherwise it has a bye); this also makes
    # the opponents of a date all different.
    for d in base:
        for i in teams:
            model.addConstr(home[d][i] + away[d][i] <= 1, name=f"one_game[{d},{i}]")

    # Double round-robin: each team plays each other team once at home and once away.
    # With the mirroring, the game on a base date and its mirror give one of each, so
    # each pair meets on exactly one base date.
    for i in teams:
        for j in teams:
            if i < j:
                model.addConstr(gp.quicksum(meets(d, i, j) for d in base) == 1, name=f"pair[{i},{j}]")

    for t in teams:
        # 2. No team plays away on both last dates.
        model.addConstr(away[n_days - 2][t] + away[n_days - 1][t] <= 1, name=f"final_aways[{t}]")

        # 3. At most two home matches in a row, at most two away matches in a row,
        # at most three away matches or byes in a row, at most four home matches or
        # byes in a row.
        for d in range(n_days - 2):
            model.addConstr(gp.quicksum(home[e][t] for e in range(d, d + 3)) <= 2)
            model.addConstr(gp.quicksum(away[e][t] for e in range(d, d + 3)) <= 2)
        for d in range(n_days - 3):
            model.addConstr(gp.quicksum(away[e][t] + bye[e][t] for e in range(d, d + 4)) <= 3)
        for d in range(n_days - 4):
            model.addConstr(gp.quicksum(home[e][t] + bye[e][t] for e in range(d, d + 5)) <= 4)

        # 4. Of the weekends, each team plays four at home, four away and has one bye.
        model.addConstr(gp.quicksum(home[d][t] for d in weekends) == 4)
        model.addConstr(gp.quicksum(away[d][t] for d in weekends) == 4)
        model.addConstr(gp.quicksum(bye[d][t] for d in weekends) == 1)

        # 5. Home matches or byes on at least two of the first five weekends.
        model.addConstr(gp.quicksum(home[d][t] + bye[d][t] for d in weekends[:5]) >= 2)

    # 6. On the last date every team except FSU plays its rival, FSU, or has a bye:
    # it meets no other team.
    last = n_days - 1
    for t in teams:
        if t != FSU:
            for j in teams:
                if j not in (t, rivals[t], FSU):
                    model.addConstr(meets(last, t, j) == 0, name=f"rival[{t},{j}]")

    # 7. Wake-UNC, Wake-Duke, GT-UNC and GT-Duke each meet at least once in dates 11 to 18.
    for a, b in ((WAKE, UNC), (WAKE, DUKE), (GT, UNC), (GT, DUKE)):
        model.addConstr(gp.quicksum(meets(d, a, b) for d in range(10, n_days)) >= 1, name=f"late[{a},{b}]")

    # 8. No team plays away against UNC and then away against Duke on consecutive dates,
    # or the other way round.
    for t in teams:
        if t not in (DUKE, UNC):
            for d in range(n_days - 1):
                model.addConstr(hosts(d, UNC, t) + hosts(d + 1, DUKE, t) <= 1)
                model.addConstr(hosts(d, DUKE, t) + hosts(d + 1, UNC, t) <= 1)
    # No team plays UNC, Duke and Wake on three consecutive dates, in any order.
    orders = [(UNC, DUKE, WAKE), (UNC, WAKE, DUKE), (DUKE, UNC, WAKE),
              (DUKE, WAKE, UNC), (WAKE, UNC, DUKE), (WAKE, DUKE, UNC)]
    for t in teams:
        if t not in (UNC, DUKE, WAKE):
            for d in range(n_days - 2):
                for x, y, z in orders:
                    model.addConstr(meets(d, t, x) + meets(d + 1, t, y) + meets(d + 2, t, z) <= 2)

    # 9. Other constraints.
    # UNC plays its rival Duke in the last date and in date 11.
    model.addConstr(meets(10, UNC, DUKE) == 1)
    model.addConstr(meets(last, UNC, DUKE) == 1)
    # UNC plays Clem in the second date.
    model.addConstr(meets(1, UNC, CLEM) == 1)
    # Duke has a bye in date 16.
    model.addConstr(bye[15][DUKE] == 1)
    # Wake does not play home in date 17.
    model.addConstr(home[16][WAKE] == 0)
    # Wake has a bye in the first date.
    model.addConstr(bye[0][WAKE] == 1)
    # Clem, Duke, UMD and Wake do not play away in the last date.
    for t in (CLEM, DUKE, UMD, WAKE):
        model.addConstr(away[last][t] == 0)
    # Clem, FSU, GT and Wake do not play away in the first date.
    for t in (CLEM, FSU, GT, WAKE):
        model.addConstr(away[0][t] == 0)
    # Neither FSU nor NCSt has a bye in the last date.
    for t in (FSU, NCST):
        model.addConstr(bye[last][t] == 0)
    # UNC does not have a bye in the first date.
    model.addConstr(bye[0][UNC] == 0)

    # config[d][i]: the opponent of team i on date d, i itself on a bye.
    # where[d][i]: 0 home, 1 bye, 2 away, which is 1 - home + away.
    config = [[gp.quicksum(j * meets(d, i, j) for j in teams if j != i) + i * bye[d][i] for i in teams]
              for d in days]
    where = [[HOME * home[d][i] + BYE * bye[d][i] + AWAY * away[d][i] for i in teams] for d in days]
    return model, {"config": config, "where": where}
