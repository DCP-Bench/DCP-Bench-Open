# Revenue maximization: choose how many units of each flight package to sell,
# subject to the passenger seats on every flight leg, to maximize total revenue.
# Each unit count is a binary encoding: units = sum of 2^k * bit_k.

from paramita.modelling import Bool


def build(instance):
    seats = instance["available_seats"]    # passenger seats per flight leg
    demand = instance["demand"]            # maximum units of each package
    revenue = instance["revenue"]          # revenue per unit of each package
    delta = instance["delta"]              # delta[j][l] = 1 if package j uses leg l

    num_packages = len(demand)
    num_legs = len(seats)

    cons = []
    units = []
    for j in range(num_packages):
        # enough bits to write every count from 0 to demand[j]
        width = max(1, demand[j].bit_length())
        bits = [Bool(f"x_{j}_bit_{k}") for k in range(width)]
        # units of package j is the binary number formed by its bits
        value = sum((2 ** k) * bits[k] for k in range(width))
        # the units sold cannot exceed the estimated demand of the package
        cons.append(value <= demand[j])
        units.append(value)

    # a flight leg has a limited number of passenger seats:
    # the seats reserved by the packages that use the leg must not exceed them
    for l in range(num_legs):
        load = sum(delta[j][l] * units[j] for j in range(num_packages) if delta[j][l])
        if not isinstance(load, int):
            cons.append(load <= seats[l])

    # the total revenue is the price of each package times the units sold
    total_revenue = sum(revenue[j] * units[j] for j in range(num_packages))

    return cons, {"packages_to_sell": units, "max_revenue": total_revenue}, ("maximize", total_revenue)
