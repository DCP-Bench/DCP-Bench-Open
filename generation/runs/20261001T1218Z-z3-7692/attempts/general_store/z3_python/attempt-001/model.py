# General store: a shopkeeper's sign shows sixteen words that add up to the word
# ALLWOOL. Each different letter stands for a different digit; find the digits.
import z3


def build(instance):
    del instance  # the puzzle states its own words

    letters = "CHESABOWPL"
    digit = {ch: z3.Int(ch) for ch in letters}

    # Problem data: the words above the line, and their total below it.
    words = ["CHESS", "CASH", "BOWWOW", "CHOPS", "ALSOPS", "PALEALE", "COOL",
             "BASS", "HOPS", "ALES", "HOES", "APPLES", "COWS", "CHEESE",
             "CHSOAP", "SHEEP"]
    total = "ALLWOOL"

    solver = z3.Solver()

    # Each letter is a digit from 0 to 9, and different letters are different digits.
    for ch in letters:
        solver.add(digit[ch] >= 0, digit[ch] <= 9)
    solver.add(z3.Distinct([digit[ch] for ch in letters]))

    def value(word):
        # The number written by the word, most significant letter first.
        return z3.Sum([digit[ch] * 10 ** k for k, ch in enumerate(reversed(word))])

    # The words add up to ALLWOOL.
    solver.add(z3.Sum([value(w) for w in words]) == value(total))

    return solver, {ch: digit[ch] for ch in letters}
