from pycsp3 import *

# Choose how many servings of each of four foods to buy, so that the diet meets the
# nutritional limits and costs as little as possible.

n = data.n
price = data.price
limits = data.limits

# nutrition per serving of each food, as in the problem statement:
# calories, chocolate (ounces), sugar (ounces), fat (ounces)
nutrition = [
    [400, 3, 2, 2],  # chocolate cake (1 slice)
    [200, 2, 2, 4],  # chocolate ice cream (1 scoop)
    [150, 0, 4, 1],  # cola (1 bottle)
    [500, 0, 4, 5],  # pineapple cheesecake (1 piece)
]

# food[k] is the number of servings of food k in the diet
food = VarArray(size=n, dom=range(0, 501))

# cost is the total price of the diet
cost = Var(dom=range(0, 500 * max(price) * n + 1))

satisfy(
    # the diet has at least the required calories
    Sum(nutrition[k][0] * food[k] for k in range(n)) >= limits[0],

    # the diet has at least the required amount of chocolate
    Sum(nutrition[k][1] * food[k] for k in range(n)) >= limits[1],

    # the diet has at least the required amount of sugar
    Sum(nutrition[k][2] * food[k] for k in range(n)) >= limits[2],

    # the diet has at least the required amount of fat
    Sum(nutrition[k][3] * food[k] for k in range(n)) >= limits[3],

    # the cost is the price of each food times its number of servings
    cost == Sum(price[k] * food[k] for k in range(n)),
)

# minimise the cost of the diet
minimize(cost)
