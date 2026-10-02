# Sports tournament scheduling: n teams play over n - 1 weeks, with n / 2 periods per week and a
# home team and an away team in each slot. Every team plays once a week, every team plays every
# other team, and every team plays at most twice in the same period over the tournament.
from itertools import combinations

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    n_teams = instance["n_teams"]
    n_weeks, n_periods = n_teams - 1, n_teams // 2
    teams = range(1, n_teams + 1)  # the teams are numbered from 1

    pool = IDPool()
    # home[w][p], away[w][p] = the home and the away team in week w, period p
    home = [[Integer(f"home_{w}_{p}", 1, n_teams, vpool=pool) for p in range(n_periods)] for w in range(n_weeks)]
    away = [[Integer(f"away_{w}_{p}", 1, n_teams, vpool=pool) for p in range(n_periods)] for w in range(n_weeks)]
    engine = IntegerEngine(vars=[t for week in home + away for t in week], vpool=pool)

    # every team plays once a week: the 2 * (n / 2) team places of a week hold different teams.
    # (This also means no team plays itself.)
    for w in range(n_weeks):
        engine.add_alldifferent(home[w] + away[w])
    cnf = engine.clausify()

    # every team plays every other team: for each pair of teams some slot has them as home and away
    # (in either order). meets[...] says "this slot is this pair, with this team at home".
    for t1, t2 in combinations(teams, 2):
        meetings = []
        for w in range(n_weeks):
            for p in range(n_periods):
                for first, second in ((t1, t2), (t2, t1)):
                    meets = pool.id(("meets", w, p, first, second))
                    cnf.append([-meets, home[w][p].equals(first)])
                    cnf.append([-meets, away[w][p].equals(second)])
                    meetings.append(meets)
        cnf.append(meetings)

    # every team plays at most twice in the same period over the tournament: plays[w][p][t] is true
    # when team t is in week w, period p (as home or away), and at most two weeks can have it
    for p in range(n_periods):
        for t in teams:
            plays = []
            for w in range(n_weeks):
                in_slot = pool.id(("plays", w, p, t))
                cnf.append([-home[w][p].equals(t), in_slot])
                cnf.append([-away[w][p].equals(t), in_slot])
                plays.append(in_slot)
            cnf.extend(CardEnc.atmost(lits=plays, bound=2, vpool=pool, encoding=EncType.seqcounter).clauses)

    return cnf, {"home": home, "away": away}
