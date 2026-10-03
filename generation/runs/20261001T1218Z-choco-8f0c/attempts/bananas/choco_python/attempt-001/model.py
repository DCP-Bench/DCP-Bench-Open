# Bananas: five bananas cost $3, seven oranges $5, nine mangoes $7 and three apples $9. Buy 100
# fruits for $100, at least one of each kind, with as few bananas and apples together as possible.
from pychoco.model import Model

# The puzzle has no instance data; prices, the 100 fruits and the $100 are its statement.
# Prices are scaled by 3*5*7*9 = 945 so that every per-fruit price is a whole number:
# banana 3/5 -> 567, orange 5/7 -> 675, mango 7/9 -> 735, apple 9/3 -> 2835.
SCALE = 945
UNIT_PRICE = [3 * SCALE // 5, 5 * SCALE // 7, 7 * SCALE // 9, 9 * SCALE // 3]
N_FRUITS = 100
BUDGET = 100


def build(instance):
    del instance  # the puzzle carries no instance data

    model = Model()

    # how many of each fruit to buy; every type is bought at least once
    bananas, oranges, mangoes, apples = x = [
        model.intvar(1, N_FRUITS, name=name) for name in ("bananas", "oranges", "mangoes", "apples")]

    # The fruits cost exactly $100 (scaled by 945).
    model.scalar(x, UNIT_PRICE, "=", BUDGET * SCALE).post()

    # Exactly 100 fruits are bought.
    model.sum(x, "=", N_FRUITS).post()

    # Minimise the number of bananas and apples together.
    disliked = model.intvar(2, 2 * N_FRUITS, name="disliked")
    model.sum([bananas, apples], "=", disliked).post()

    return (model,
            {"bananas": bananas, "oranges": oranges, "mangoes": mangoes, "apples": apples},
            ("minimize", disliked))
