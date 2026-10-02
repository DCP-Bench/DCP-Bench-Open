# Bananas: five bananas cost 3 dollars, seven oranges 5, nine mangoes 7 and three apples 9. Buy
# 100 fruits for 100 dollars, at least one of each, with as few bananas and apples as possible.
from exact import Exact


def build(instance):
    # This problem has no instance data. The prices and the totals belong to the problem statement.
    solver = Exact()

    # quantities of each fruit, between 1 and 100 (all types must be bought)
    fruits = ["bananas", "oranges", "mangoes", "apples"]
    for name in fruits:
        solver.addVariable(name, 1, 100)

    # the_sum = number of bananas and apples bought, which should be minimal
    solver.addVariable("the_sum", 1, 2000)
    solver.addConstraint([(1, "bananas"), (1, "apples"), (-1, "the_sum")], True, 0, True, 0)

    # total cost is 100 dollars. Prices per fruit are 3/5, 5/7, 7/9 and 9/3 dollars; multiplying
    # both sides by 3*5*7*9 = 945 removes the fractions: 189*3, 135*5, 105*7, 315*9 and 100*945.
    solver.addConstraint([(3 * 189, "bananas"), (5 * 135, "oranges"), (7 * 105, "mangoes"),
                          (9 * 315, "apples")], True, 100 * 945, True, 100 * 945)

    # 100 fruits in total
    solver.addConstraint([(1, name) for name in fruits], True, 100, True, 100)

    # minimise the number of bananas and apples
    return solver, {name: name for name in fruits}, ("minimize", [(1, "the_sum")])
