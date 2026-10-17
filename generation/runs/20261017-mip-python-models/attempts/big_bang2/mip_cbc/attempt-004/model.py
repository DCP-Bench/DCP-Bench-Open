# Problem big_bang2: nontransitive dice. Five dice with six faces each, face values 1..12,
# where die A beats die B when A has a strictly larger face than B in more than half of
# the 36 face pairs. The beats relations follow Rock-Paper-Scissors-Lizard-Spock.
import mip

# Dice index: 0 Rock, 1 Paper, 2 Scissors, 3 Lizard, 4 Spock.
BEATS = [
    (0, 2),  # Rock crushes Scissors
    (0, 3),  # Rock crushes Lizard
    (1, 0),  # Paper covers Rock
    (1, 4),  # Paper disproves Spock
    (2, 1),  # Scissors cuts Paper
    (2, 3),  # Scissors decapitate Lizard
    (3, 1),  # Lizard eats Paper
    (3, 4),  # Lizard poisons Spock
    (4, 0),  # Spock vaporizes Rock
    (4, 2),  # Spock smashes Scissors
]
N_DICE = 5
N_FACES = 6
MAX_VAL = 12
WIN_NEEDED = 19  # strictly more than half of the 36 face pairs


def build(instance):
    model = mip.Model(solver_name="CBC")

    # Order (thermometer) encoding: ge[i][j][t] = 1 iff face j of die i is at least t,
    # for t = 2..12. Value 1 is the base, so value = 1 + sum_t ge[t].
    ge = {}
    for i in range(N_DICE):
        for j in range(N_FACES):
            for t in range(2, MAX_VAL + 1):
                ge[i, j, t] = model.add_var(f"ge_{i}_{j}_{t}", var_type=mip.BINARY)
            for t in range(2, MAX_VAL):
                model.add_constr(ge[i, j, t + 1] <= ge[i, j, t])

    def value(i, j):
        return 1 + mip.xsum(ge[i, j, t] for t in range(2, MAX_VAL + 1))

    # Each beats relation: 36 face pairs, win binary per pair with win = 1 only if the
    # winner face is strictly larger than the loser face.
    # For each t in 1..12: (loser >= t) implies (winner >= t + 1).
    # At t = 1 the loser term is constant 1; at t = 12 the winner term (>= 13) is constant 0.
    for r, (w_die, l_die) in enumerate(BEATS):
        wins = []
        for a in range(N_FACES):
            for b in range(N_FACES):
                win = model.add_var(f"win_{r}_{a}_{b}", var_type=mip.BINARY)
                wins.append(win)
                for t in range(1, MAX_VAL + 1):
                    # win + atleast(loser, t) - atleast(winner, t + 1) <= 1
                    terms = [(win, 1)]
                    const = 0
                    if t == 1:
                        const += 1
                    else:
                        terms.append((ge[l_die, b, t], 1))
                    if t + 1 <= MAX_VAL:
                        terms.append((ge[w_die, a, t + 1], -1))
                    lhs = mip.xsum(c * v for v, c in terms)
                    model.add_constr(lhs <= 1 - const)
        model.add_constr(mip.xsum(wins) >= WIN_NEEDED)

    dice = [[value(i, j) for j in range(N_FACES)] for i in range(N_DICE)]
    return model, {"dice": dice}
