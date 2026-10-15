# Facility location: choose which of four warehouses to open and how many units each open warehouse ships to each region, minimising total cost.
from paramita.modelling import Bool, If, Or


def build(instance):
    cities = instance["warehouse_s"]
    fixed = instance["fixed_costs"]
    cost = instance["shipping_costs"]
    demands = instance["demands"]
    cap = instance["max_shipping"]
    n_w, n_r = len(cities), len(demands)
    ny, la, atl = cities.index("New York"), cities.index("Los Angeles"), cities.index("Atlanta")

    # open[i] = 1 if warehouse i is opened
    open_ = [Bool(f"open_{i}") for i in range(n_w)]

    # Shipped amounts are binary numbers: ships[i][j] = sum of 2^k * bit[i][j][k].
    # Units never exceed max_shipping, so max_shipping.bit_length() bits are enough.
    nbits = max(1, cap.bit_length())
    bits = [[[Bool(f"ship_{i}_{j}_b{k}") for k in range(nbits)] for j in range(n_r)] for i in range(n_w)]
    ships = [[sum((1 << k) * bits[i][j][k] for k in range(nbits)) for j in range(n_r)] for i in range(n_w)]

    cons = []

    # If the New York warehouse is opened, then the Los Angeles warehouse must also be opened.
    cons.append(If(open_[ny], open_[la]))

    # No more than three warehouses can be operational.
    cons.append(sum(open_) <= 3)

    # Either the Atlanta or the Los Angeles warehouse must be opened.
    cons.append(Or([open_[atl], open_[la]]))

    # Every region's demand is met by the shipments from all warehouses together.
    for j in range(n_r):
        cons.append(sum(ships[i][j] for i in range(n_w)) == demands[j])

    # An open warehouse ships at most max_shipping units in total; a closed one ships nothing.
    for i in range(n_w):
        cons.append(sum(ships[i][j] for j in range(n_r)) <= cap * open_[i])

    # Total cost: fixed costs of the opened warehouses plus the shipping costs.
    fixed_part = sum(fixed[i] * open_[i] for i in range(n_w))
    ship_part = sum(cost[i][j] * ships[i][j] for i in range(n_w) for j in range(n_r))
    total = fixed_part + ship_part

    outputs = {
        "open_warehouse": open_,
        "ships": ships,
        "total_cost": total,
    }
    return cons, outputs, ("minimize", total)
