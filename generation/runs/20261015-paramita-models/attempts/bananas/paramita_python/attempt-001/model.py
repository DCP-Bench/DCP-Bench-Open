# Fruit shopping: buy 100 fruits for exactly 100 dollars, every type at least once,
# minimising the number of bananas and apples.
# Prices are problem data from the statement, scaled to integers: 1 unit = 1/315 dollar,
# since 315 = lcm(5, 7, 9, 3) makes every per-fruit price whole.
# Each quantity is unary: ge[f][k] means "at least k fruits of type f", for k = 2..MAX.
from paramita.modelling import Bool, If

PRICE = {"bananas": 189, "oranges": 225, "mangoes": 245, "apples": 945}  # per fruit, 1/315 dollar
BUDGET = 100 * 315  # 100 dollars
TOTAL = 100  # fruits to purchase
MAX_ONE_TYPE = TOTAL - 3  # each of the other three types takes at least one fruit


def build(instance):
    ge = {f: {k: Bool(f"{f}_ge_{k}") for k in range(2, MAX_ONE_TYPE + 1)} for f in PRICE}
    cons = []

    # a quantity of at least k implies at least k-1 (unary order)
    for f in PRICE:
        for k in range(2, MAX_ONE_TYPE):
            cons.append(If(ge[f][k + 1], ge[f][k]))

    # each type is bought at least once, so the quantity is 1 plus the count of true bits
    val = {f: 1 + sum(ge[f].values()) for f in PRICE}

    # 100 fruits in total
    cons.append(sum(val.values()) == TOTAL)

    # spend exactly 100 dollars: the constant part of each price is already in the 1 per type
    cons.append(sum(PRICE[f] * ge[f][k] for f in PRICE for k in ge[f]) == BUDGET - sum(PRICE.values()))

    outputs = {"apples": val["apples"], "bananas": val["bananas"],
               "mangoes": val["mangoes"], "oranges": val["oranges"]}

    # minimise the quantity of bananas and apples
    objective = val["bananas"] + val["apples"]
    return cons, outputs, ("minimize", objective)
