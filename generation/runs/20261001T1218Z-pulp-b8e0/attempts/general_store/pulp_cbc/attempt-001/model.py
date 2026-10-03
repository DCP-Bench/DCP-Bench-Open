"""General store: an alphametic in which sixteen words (CHESS, CASH, BOWWOW, ...) add up to
ALLWOOL, each letter standing for a different digit.

The model reports the digit of each letter C, H, E, S, A, B, O, W, P, L.
"""
import pulp


def build(instance):
    del instance  # the puzzle has no instance data; its words are below

    letters = ["C", "H", "E", "S", "A", "B", "O", "W", "P", "L"]
    # the words of the sign, mirrored from the reference
    addends = ["CHESS", "CASH", "BOWWOW", "CHOPS", "ALSOPS", "PALEALE", "COOL", "BASS",
               "HOPS", "ALES", "HOES", "APPLES", "COWS", "CHEESE", "CHSOAP", "SHEEP"]
    total = "ALLWOOL"
    digits = range(10)

    problem = pulp.LpProblem("general_store", pulp.LpMinimize)  # satisfaction

    # is_digit[letter][v] = 1 if the letter stands for digit v; each letter has one digit
    # and different letters have different digits
    is_digit = {ch: [pulp.LpVariable(f"is_{ch}_{v}", cat="Binary") for v in digits]
                for ch in letters}
    for ch in letters:
        problem += pulp.lpSum(is_digit[ch]) == 1
    for v in digits:
        problem += pulp.lpSum(is_digit[ch][v] for ch in letters) <= 1
    value = {ch: pulp.lpSum(v * is_digit[ch][v] for v in digits) for ch in letters}

    def number(word):
        return pulp.lpSum(10 ** (len(word) - 1 - k) * value[ch] for k, ch in enumerate(word))

    # the words above the line add up to ALLWOOL
    problem += pulp.lpSum(number(word) for word in addends) == number(total)

    return problem, value
