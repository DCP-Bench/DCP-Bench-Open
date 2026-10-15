# Revenue maximization: choose how many units of each flight package to sell,
# subject to the passenger seats on every flight leg, to maximize total revenue.
# Integers are unary (order) encodings: x_j_ge_k means "units of package j >= k".

from paramita.modelling import Bool, If


def build(instance):
    seats = instance["available_seats"]    # passenger seats per flight leg
    demand = instance["demand"]            # maximum units of each package
    revenue = instance["revenue"]          # revenue per unit of each package
    delta = instance["delta"]              # delta[j][l] = 1 if package j uses leg l

    num_packages = len(demand)
    num_legs = len(seats)

    # Units sold of package j, in 0..demand[j], as a unary sum of Bools.
    # bits[j][k-1] is the Bool "units of package j >= k".
    bits = [[Bool(f"x_{j}_ge_{k}") for k in range(1, demand[j] + 1)] for j in range(num_packages)]
    cons = []
    # the units sold of a package are ordered: at least k+1 units implies at least k units
    for j in range(num_packages):
        for k in range(1, demand[j]):
            cons.append(If(bits[j][k], bits[j][k - 1]))
    units = [sum(bits[j]) for j in range(num_packages)]

    # a flight leg has a limited number of passenger seats:
    # the seats reserved by the packages that use the leg must not exceed them
    for l in range(num_legs):
        load = sum(delta[j][l] * units[j] for j in range(num_packages) if delta[j][l])
        if not isinstance(load, int):
            cons.append(load <= seats[l])

    # the total revenue is the price of each package times the units sold
    total_revenue = sum(revenue[j] * units[j] for j in range(num_packages))

    return cons, {"packages_to_sell": units, "max_revenue": total_revenue}, ("maximize", total_revenue)
