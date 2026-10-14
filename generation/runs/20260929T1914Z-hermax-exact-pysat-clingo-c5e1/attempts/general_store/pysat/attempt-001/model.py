# General store: each letter of the sign stands for a different digit, and the
# sixteen words above the line add up to ALL WOOL.
from collections import Counter
from functools import reduce
from operator import add

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine

WORDS = ["CHESS", "CASH", "BOWWOW", "CHOPS", "ALSOPS", "PALEALE", "COOL", "BASS",
         "HOPS", "ALES", "HOES", "APPLES", "COWS", "CHEESE", "CHSOAP", "SHEEP"]
TOTAL = "ALLWOOL"


def build(instance):
    # The puzzle is fixed by the problem; the instance carries no data.
    letters = sorted(set("".join(WORDS) + TOTAL))
    width = len(TOTAL)

    pool = IDPool()
    # digit[letter] = the digit the letter stands for
    digit = {letter: Integer(letter, 0, 9, vpool=pool) for letter in letters}
    # carry[k] is what column k passes on to column k + 1; at most 15 as a column adds 16 digits
    carry = [Integer(f"carry_{k}", 0, 15, vpool=pool) for k in range(width - 1)]
    engine = IntegerEngine(vars=list(digit.values()) + carry, vpool=pool)

    # every letter stands for a different digit
    engine.add_alldifferent(list(digit.values()))

    # The addition is done column by column, from the units up.
    for k in range(width):
        # how many times each letter is added in column k, less one for the letter of the total
        net = Counter(word[-1 - k] for word in WORDS if len(word) > k)
        net[TOTAL[-1 - k]] -= 1
        left = [count * digit[letter] for letter, count in net.items() if count > 0]
        right = [-count * digit[letter] for letter, count in net.items() if count < 0]
        # digits of column k + carry in = digit of the total + 10 * carry out
        if k > 0:
            left.append(carry[k - 1])
        if k < width - 1:
            right.append(10 * carry[k])
        engine.add_linear(reduce(add, left) == reduce(add, right))

    return engine.clausify(), {letter: digit[letter] for letter in letters}
