# Fixed-charge production: a company makes products that each need labor and
# cloth (both in limited supply) and can only be made on a rented machine.
# Choose which machines to rent and how many of each product to make so that the
# profit from the products, less the machine rental costs, is as large as possible.
import functools
import operator

from hermax.model import Model


def add_term(m, prev, prev_hi, lit, weight, name):
    """Return (s, s_hi) with s = prev + weight * [lit], and 0 <= s <= s_hi.

    prev is an integer variable with range [0, prev_hi], or None for the value 0.
    s is tied to prev and lit in both directions, one clause set per value t of
    s (hermax gives each integer the literals "s >= t"). Chaining such terms adds
    up a weighted sum of literals exactly while every integer stays narrow.
    """
    s_hi = prev_hi + weight
    s = m.int(name, 0, s_hi)

    def prev_ge(t):  # the literal "prev >= t", or True / False when already settled
        if t <= 0:
            return True
        if t > prev_hi:
            return False
        return prev >= t

    def neg(x):
        return (not x) if isinstance(x, bool) else ~x

    def post(*lits):  # clause over literals; a True disjunct satisfies it, False ones drop out
        nonlocal m
        kept = []
        for x in lits:
            if x is True:
                return
            if x is not False:
                kept.append(x)
        m &= functools.reduce(operator.or_, kept)

    for t in range(1, s_hi + 1):
        at_least = s >= t
        post(neg(prev_ge(t)), at_least)  # prev >= t makes s >= t
        post(~lit, neg(prev_ge(t - weight)), at_least)  # lit and prev >= t - weight make s >= t
        post(~at_least, prev_ge(t), lit)  # s >= t needs prev >= t or lit
        post(~at_least, prev_ge(t - weight))  # s >= t needs prev >= t - weight
    return s, s_hi


def build(instance):
    renting_cost = instance["renting_cost"]  # renting_cost[k] = cost of renting machine k
    capacity = instance["capacity"]  # capacity[r] = available amount of resource r (labor, cloth)
    max_production = instance["max_production"]  # most units of one product the problem allows
    product = instance["product"]  # product[p] = [profit per unit, machine needed]
    use = instance["use"]  # use[p][r] = amount of resource r that one unit of p uses
    num_products = len(product)
    num_machines = len(renting_cost)
    num_resources = len(capacity)
    profit = [product[p][0] for p in range(num_products)]
    machine = [product[p][1] for p in range(num_products)]

    # No product can be made in more units than its scarcest resource allows
    # (or than max_production); this is implied by the capacity constraints and
    # keeps the numbers small.
    bound = []
    for p in range(num_products):
        limit = max_production
        for r in range(num_resources):
            if use[p][r] > 0:
                limit = min(limit, capacity[r] // use[p][r])
        bound.append(max(limit, 1))

    m = Model()
    # rent[k] = machine k is rented
    rent = m.bool_vector("rent", num_machines)
    # The units of product p are written in binary: bit[p][b] is the digit worth
    # 2^b, so produce[p] = sum of 2^b * bit[p][b]. Binary digits keep the number
    # of variables, and of weighted terms below, small however many units there are.
    bit = [m.bool_vector(f"bit_{p}", bound[p].bit_length()) for p in range(num_products)]

    # no product is made in more units than its bound
    for p in range(num_products):
        m &= (sum(2 ** b * bit[p][b] for b in range(len(bit[p]))) <= bound[p])

    # resource use stays within what is available
    for r in range(num_resources):
        m &= (sum(use[p][r] * 2 ** b * bit[p][b]
                  for p in range(num_products) for b in range(len(bit[p]))) <= capacity[r])

    # a product can only be made when the machine it needs is rented
    for p in range(num_products):
        for b in range(len(bit[p])):
            m &= (~bit[p][b] | rent[machine[p]])

    # Maximise profit minus rental costs. A soft clause pays when its literal is
    # false: a binary digit that is off loses the profit of the units it stands for
    # (literal "bit"), and renting a machine costs its rent (literal "not rent").
    # The total paid is a constant minus the profit, so minimising it maximises it.
    for p in range(num_products):
        for b in range(len(bit[p])):
            m.obj[profit[p] * 2 ** b] += bit[p][b]
    for k in range(num_machines):
        m.obj[renting_cost[k]] += ~rent[k]

    # z is the declared output: the profit made. It is added up exactly with a chain
    # of additions of one weighted literal each: profit * 2^b for every digit that
    # is on, plus renting_cost[k] for every machine that is NOT rented. That total
    # is the revenue plus all rents minus the rents paid, so z is the total
    # less the sum of all the rents.
    terms = ([(profit[p] * 2 ** b, bit[p][b]) for p in range(num_products) for b in range(len(bit[p]))
              if profit[p] > 0]
             + [(renting_cost[k], ~rent[k]) for k in range(num_machines) if renting_cost[k] > 0])
    terms.sort(key=lambda term: term[0])
    all_rents = sum(renting_cost)
    total, total_hi = None, 0
    for i, (weight, literal) in enumerate(terms):
        total, total_hi = add_term(m, total, total_hi, literal, weight, f"partial_{i}")
    z = m.int("z", 0, max(total_hi - all_rents, 1))
    m &= (total - z == all_rents)

    return m, {"z": z}
