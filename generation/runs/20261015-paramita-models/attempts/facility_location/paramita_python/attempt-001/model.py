# Facility location: choose which warehouses to open and how many units each
# open warehouse ships to each region, minimising fixed plus shipping costs.
# Integers (shipments) are unary (order) encodings: ge[i][j][k] means
# "units shipped from warehouse i to region j are at least k". Shipments are
# summed, bounded and compared, so the unary form fits better than one-hot.
from paramita.modelling import Bool, If


def build(instance):
    cities = instance["warehouse_s"]
    cap = instance["max_shipping"]          # capacity of each warehouse
    demands = instance["demands"]           # demand of each region
    fixed = instance["fixed_costs"]         # fixed cost of opening each warehouse
    unit_cost = instance["shipping_costs"]  # unit shipping cost, warehouse x region
    W, R = len(cities), len(demands)
    city = {name: i for i, name in enumerate(cities)}
    new_york, los_angeles, atlanta = city["New York"], city["Los Angeles"], city["Atlanta"]

    # open[i] = 1 if the warehouse in city i is opened
    open_w = [Bool(f"open_{i}") for i in range(W)]

    # ship unary bits: ge[i][j][k-1] = 1 if shipments from i to region j are >= k.
    # A shipment never exceeds the warehouse capacity or the region demand, so the
    # number of bits is min(capacity, demand) per pair.
    ge = [[[Bool(f"ship_{i}_{j}_ge_{k}") for k in range(1, min(cap, demands[j]) + 1)]
           for j in range(R)] for i in range(W)]

    def ship(i, j):
        return sum(ge[i][j])

    cons = []
    # the unary bits of one shipment value are ordered: at least k+1 implies at least k
    for i in range(W):
        for j in range(R):
            bits = ge[i][j]
            cons += [If(bits[k + 1], bits[k]) for k in range(len(bits) - 1)]

    # each region's demand is met exactly by the shipments of all warehouses together
    cons += [sum(ship(i, j) for i in range(W)) == demands[j] for j in range(R)]

    # an open warehouse ships at most its capacity; a closed one ships nothing
    cons += [sum(ship(i, j) for j in range(R)) <= cap * open_w[i] for i in range(W)]

    # if the New York warehouse is opened, then the Los Angeles warehouse must also be opened
    cons.append(If(open_w[new_york], open_w[los_angeles]))

    # no more than three warehouses can be operational in any given week
    cons.append(sum(open_w) <= 3)

    # either the Atlanta or the Los Angeles warehouse must be opened
    cons.append(open_w[atlanta] | open_w[los_angeles])

    # total cost = fixed costs of the opened warehouses + unit shipping cost times units shipped
    total = (sum(fixed[i] * open_w[i] for i in range(W))
             + sum(unit_cost[i][j] * bit for i in range(W) for j in range(R) for bit in ge[i][j]))

    outputs = {
        "open_warehouse": open_w,
        "ships": [[ship(i, j) for j in range(R)] for i in range(W)],
        "total_cost": total,
    }
    return cons, outputs, ("minimize", total)
