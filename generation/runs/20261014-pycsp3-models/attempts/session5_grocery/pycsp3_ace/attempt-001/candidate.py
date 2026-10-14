from pycsp3 import *

num_items = data.num_items
total = data.total_price  # the total price in cents

# the cashier's product: the items multiplied, in dollars, equals the total in cents,
# so in cents the product of the prices is the total times 100 for each item after the first
product = total * 100 ** (num_items - 1)

# every price divides the product of all prices, and so is one of its divisors up to the total
divisors = [d for d in range(1, total + 1) if product % d == 0]
prices = VarArray(size=num_items, dom=divisors)

satisfy(
    # the items added up give the total price
    Sum(prices) == total,
    # the items multiplied give the same total price
    Product(prices) == product,
    # the items are listed in increasing order of price
    Increasing(prices, strict=False),
)
