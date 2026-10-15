"""Facility location: choose which warehouses to open and how many units each
open warehouse ships to each region, minimising fixed plus shipping costs.

Shipment integers are binary encoded: ship_bits[i][j][k] has weight 2**k in the
shipment from warehouse i to region j.
"""

from paramita.modelling import Bool, If, Or


def binary(name, ub):
    """Binary encoding of an integer in 0..ub, returned as (weight, bit) pairs."""
    nbits = max(1, ub.bit_length())
    return [(2**k, Bool(f"{name}_bit_{k}")) for k in range(nbits)]


def build(instance):
    cities = instance["warehouse_s"]
    demands = instance["demands"]
    fixed_costs = instance["fixed_costs"]
    max_shipping = instance["max_shipping"]
    shipping_costs = instance["shipping_costs"]

    n_w = len(cities)
    n_r = len(demands)

    # Warehouse indices are looked up by city name from the instance.
    ny = cities.index("New York")
    la = cities.index("Los Angeles")
    atl = cities.index("Atlanta")

    # open_w[i] is true when warehouse i is opened.
    open_w = [Bool(f"open_{i}") for i in range(n_w)]

    cons = []

    # ships[i][j]: units shipped from warehouse i to region j.
    # A single shipment never exceeds the warehouse capacity or the demand, and
    # is 0 when warehouse i is closed (redundant with the capacity rule below,
    # but it lets the solver propagate closures per lane).
    ship = [[None] * n_r for _ in range(n_w)]
    for i in range(n_w):
        for j in range(n_r):
            ub = min(max_shipping, demands[j])
            wb = binary(f"ship_{i}_{j}", ub)
            ship[i][j] = sum(w * b for w, b in wb)
            cons.append(ship[i][j] <= ub * open_w[i])

    # Restriction 1: if the New York warehouse is opened, then the Los Angeles
    # warehouse must also be opened.
    cons.append(If(open_w[ny], open_w[la]))

    # Restriction 2: no more than three warehouses can be operational.
    cons.append(sum(open_w) <= 3)

    # Restriction 3: either the Atlanta or the Los Angeles warehouse must be opened.
    cons.append(Or([open_w[atl], open_w[la]]))

    # A warehouse ships at most max_shipping units in total.
    for i in range(n_w):
        cons.append(sum(ship[i][j] for j in range(n_r)) <= max_shipping * open_w[i])

    # Every region receives exactly its demand from the warehouses.
    for j in range(n_r):
        cons.append(sum(ship[i][j] for i in range(n_w)) == demands[j])

    # Total cost: fixed costs of the opened warehouses plus shipping costs.
    total = sum(fixed_costs[i] * open_w[i] for i in range(n_w)) + sum(
        shipping_costs[i][j] * ship[i][j] for i in range(n_w) for j in range(n_r)
    )

    outputs = {
        "open_warehouse": open_w,
        "ships": ship,
        "total_cost": total,
    }
    return cons, outputs, ("minimize", total)
