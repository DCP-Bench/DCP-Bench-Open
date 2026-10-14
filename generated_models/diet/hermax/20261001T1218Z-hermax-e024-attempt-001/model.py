# Diet problem: buy whole servings of four foods (chocolate cake, chocolate ice
# cream, cola, pineapple cheesecake) so that the diet meets minimum amounts of
# calories, chocolate, sugar and fat, at the lowest total price.
from hermax.model import Model

# What one serving of each food contains. These come from the problem statement
# (the nutrition table), not from the instance; the instance gives prices and
# the required minimum of each nutrient.
CALORIES = [400, 200, 150, 500]
CHOCOLATE = [3, 2, 0, 0]
SUGAR = [2, 2, 4, 4]
FAT = [2, 4, 1, 5]
NUTRIENTS = [CALORIES, CHOCOLATE, SUGAR, FAT]


def build(instance):
    n = instance["n"]  # number of foods
    price = instance["price"]  # price of one serving, in cents
    limits = instance["limits"]  # required minimum of each nutrient, in nutrient order above

    # Upper bound on the servings of a food. An optimal diet never has more
    # servings of a food than this: if it did, then for every nutrient the food
    # contains, one serving less would still meet the minimum from that food alone,
    # so removing a serving keeps the diet valid and does not cost more. The bound
    # is the most servings any single nutrient could still ask for. Hermax encodes
    # integer variables, so a tight bound keeps the model small.
    def servings_bound(i):
        needed = [-(-limits[k] // NUTRIENTS[k][i]) for k in range(len(NUTRIENTS)) if NUTRIENTS[k][i] > 0]
        return max([1] + needed)

    bounds = [servings_bound(i) for i in range(n)]

    m = Model()
    # x[i] = servings of food i
    x = m.int_vector("x", n, 0, max(bounds))
    for i in range(n):
        m &= (x[i] <= bounds[i])

    # the diet meets the minimum of every nutrient
    for k in range(len(NUTRIENTS)):
        m &= (sum(NUTRIENTS[k][i] * x[i] for i in range(n)) >= limits[k])

    # Minimise the price. A soft clause pays when its literal is false, so the
    # price of the s-th serving of a food is charged on the negation of "x[i] >= s":
    # a diet with x[i] servings breaks exactly x[i] clauses of weight price[i].
    for i in range(n):
        for s in range(1, bounds[i] + 1):
            m.obj[price[i]] += ~(x[i] >= s)

    # cost is the declared output: the total price of the diet. Its range is the
    # price of the largest diet the bounds allow, so the sum stays small to encode.
    cost = m.int("cost", 0, sum(price[i] * bounds[i] for i in range(n)))
    m &= (sum(price[i] * x[i] for i in range(n)) == cost)

    return m, {"cost": cost}
