# Facility location: choose which warehouses to open and how many units each
# open warehouse ships to each region, minimising fixed plus shipping costs.
# Shipments are integers in binary (bit k has weight 2^k). Each shipment value is at
# most the capacity (max_shipping), so NBITS bits cover every value. The binary form
# keeps the number of Bools and the objective weights small, after the unary form timed out.
from paramita.modelling import Bool


def build(instance):
    cities = instance["warehouse_s"]
    cap = instance["max_shipping"]          # capacity of each warehouse
    demands = instance["demands"]           # demand of each region
    fixed = instance["fixed_costs"]         # fixed cost of opening each warehouse
    unit_cost = instance["shipping_costs"]  # unit shipping cost, warehouse x region
    W, R = len(cities), len(demands)
    city = {name: i for i, name in enumerate(cities)}
    new_york, los_angeles, atlanta = city["New York"], city["Los Angeles"], city["Atlanta"]

    # number of bits so that 2^NBITS - 1 >= every shipment value (capacity and demands)
    NBITS = max([cap] + demands).bit_length()

    # open[i] = 1 if the warehouse in city i is opened
    open_w = [Bool(f"open_{i}") for i in range(W)]

    # bit[i][j][k] = bit k (weight 2^k) of the units shipped from warehouse i to region j
    bit = [[[Bool(f"ship_{i}_{j}_bit_{k}") for k in range(NBITS)]
            for j in range(R)] for i in range(W)]

    def ship(i, j):
        return sum((1 << k) * bit[i][j][k] for k in range(NBITS))

    cons = []
    # each region's demand is met exactly by the shipments of all warehouses together
    cons += [sum(ship(i, j) for i in range(W)) == demands[j] for j in range(R)]

    # an open warehouse ships at most its capacity; a closed one ships nothing
    cons += [sum(ship(i, j) for j in range(R)) <= cap * open_w[i] for i in range(W)]

    # if the New York warehouse is opened, then the Los Angeles warehouse must also be opened
    cons.append(open_w[new_york] <= open_w[los_angeles])

    # no more than three warehouses can be operational in any given week
    cons.append(sum(open_w) <= 3)

    # either the Atlanta or the Los Angeles warehouse must be opened
    cons.append(open_w[atlanta] | open_w[los_angeles])

    # total cost = fixed costs of the opened warehouses + unit shipping cost times units shipped
    total = (sum(fixed[i] * open_w[i] for i in range(W))
             + sum(unit_cost[i][j] * (1 << k) * bit[i][j][k]
                   for i in range(W) for j in range(R) for k in range(NBITS)))

    outputs = {
        "open_warehouse": open_w,
        "ships": [[ship(i, j) for j in range(R)] for i in range(W)],
        "total_cost": total,
    }
    return cons, outputs, ("minimize", total)
