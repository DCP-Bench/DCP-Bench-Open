# general_store: cryptarithm. Each letter stands for a different digit.
# The words above the line add up to ALL WOOL. Print the values of C, H, E, S, A, B, O, W, P, L.
import cvc5.pythonic as cz


def word_value(letters):
    # Value of a word whose letters are digit variables, most significant first.
    total = 0
    for letter in letters:
        total = total * 10 + letter
    return total


def build(instance):
    C, H, E, S, A, B, O, W, P, L = cz.Ints("C H E S A B O W P L")
    letters = [C, H, E, S, A, B, O, W, P, L]

    constraints = []

    # Each letter is a digit from 0 to 9.
    for v in letters:
        constraints += [v >= 0, v <= 9]

    # Each different letter stands for a different digit.
    constraints.append(cz.Distinct(letters))

    # The leading letter of each word is not zero.
    # Leading letters: C, B, A, P, H, S.
    for v in [C, B, A, P, H, S]:
        constraints.append(v >= 1)

    # The words above the horizontal line add up to ALL WOOL.
    # The sum of the words, column by column, equals the total.
    words = [
        [C, H, E, S, S],          # CHESS
        [C, A, S, H],             # CASH
        [B, O, W, W, O, W],       # BOWWOW
        [C, H, O, P, S],          # CHOPS
        [A, L, S, O, P, S],       # ALSOPS
        [P, A, L, E, A, L, E],    # PALEALE
        [C, O, O, L],             # COOL
        [B, A, S, S],             # BASS
        [H, O, P, S],             # HOPS
        [A, L, E, S],             # ALES
        [H, O, E, S],             # HOES
        [A, P, P, L, E, S],       # APPLES
        [C, O, W, S],             # COWS
        [C, H, E, E, S, E],       # CHEESE
        [C, H, S, O, A, P],       # CHSOAP
        [S, H, E, E, P],          # SHEEP
    ]
    total = [A, L, L, W, O, O, L]  # ALLWOOL

    # Sum of the summands equals the total.
    constraints.append(
        cz.Sum([word_value(w) for w in words]) == word_value(total)
    )

    outputs = {"A": A, "B": B, "C": C, "E": E, "H": H, "L": L, "O": O, "P": P, "S": S, "W": W}
    return constraints, outputs
