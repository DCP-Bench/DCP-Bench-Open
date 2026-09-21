# Cheapest diet meeting every nutritional minimum.
#
# Servings range over 0..10000, which a one-hot encoding could not afford but
# Exact declares as bounds.
from dcp_pb import Pb


def build(instance):
    price = instance["price"]
    limits = instance["limits"]
    n = instance["n"]

    # The macro table belongs to the problem statement, not to the instance:
    # calories, chocolate, sugar and fat per serving of each of the four foods.
    macros = [
        [400, 200, 150, 500],
        [3, 2, 0, 0],
        [2, 2, 4, 4],
        [2, 4, 1, 5],
    ]

    pb = Pb()
    # 0..10000 servings and 0..1000 cents are the bounds the reference declares.
    x = pb.ints(n, 0, 10000)
    for row, least in zip(macros, limits):
        pb.ge(list(zip(row, x)), least)

    cost = pb.int(0, 1000)
    pb.eq(list(zip(price, x)) + [(-1, cost)], 0)
    pb.minimise([(1, cost)])
    return pb, {"cost": cost}
