# Big Bang (nontransitive dice): five dice with six faces each, face values 1..12, such that the
# "beats" relation between the dice is that of Rock-Paper-Scissors-Lizard-Spock. Die A beats
# die B when A shows a strictly larger face than B in more than half of all pairs of faces.
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    # Constants of the problem statement: the dice (rock, paper, scissors, lizard, spock), the
    # number of faces, the largest face value and the ten "beats" relationships.
    rock, paper, scissors, lizard, spock = 0, 1, 2, 3, 4
    m = 5   # number of dice
    n = 6   # number of faces of each die
    f = 12  # largest face value
    edge = [
        (rock, scissors),     # rock crushes scissors
        (rock, lizard),       # rock crushes lizard
        (paper, rock),        # paper covers rock
        (paper, spock),       # paper disproves spock
        (scissors, paper),    # scissors cuts paper
        (scissors, lizard),   # scissors decapitate lizard
        (lizard, paper),      # lizard eats paper
        (lizard, spock),      # lizard poisons spock
        (spock, rock),        # spock vaporizes rock
        (spock, scissors),    # spock smashes scissors
    ]

    pool = IDPool()
    # dice[i][j] = the value of face j of die i. The coupled encoding gives both the "= v" and
    # the ">= v" literals: the first is what the runner blocks an answer with, the second is
    # what the comparisons below are written with.
    dice = [[Integer(f"dice{i}_{j}", 1, f, encoding="coupled", vpool=pool) for j in range(n)]
            for i in range(m)]
    engine = IntegerEngine(vars=[face for die in dice for face in die], vpool=pool)
    cnf = engine.clausify()

    # For every "winner beats loser" relationship, the pairs of faces (x of the winner, y of the
    # loser) where the winner's face is strictly larger have to be more than half of all pairs.
    for winner, loser in edge:
        wins = []
        for x in range(n):
            for y in range(n):
                a, b = dice[winner][x], dice[loser][y]
                # wins_pair can only be true when a > b: a must be at least 2, and if b >= v
                # (for v up to f) then a >= v + 1
                wins_pair = pool.id(("wins", winner, loser, x, y))
                cnf.append([-wins_pair, a.ge(2)])
                for v in range(2, f):
                    cnf.append([-wins_pair, -b.ge(v), a.ge(v + 1)])
                cnf.append([-wins_pair, -b.ge(f)])
                wins.append(wins_pair)
        cnf.extend(CardEnc.atleast(lits=wins, bound=(n * n) // 2 + 1, vpool=pool,
                                   encoding=EncType.seqcounter).clauses)

    return cnf, {"dice": dice}
