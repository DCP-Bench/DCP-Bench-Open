"""KenKen: fill an n x n grid with the digits 1..n so that every row and every column holds
each digit once and every cage (a group of cells) satisfies its target number. Digits may
repeat inside a cage. A cage of two cells reaches its target by sum, product, difference or
exact quotient; any other cage reaches it by sum or by product of its digits.

The model reports the filled grid.
"""
import pulp


def build(instance):
    n = instance["n"]  # grid size, digits are 1..n
    cages = instance["problem"]  # each cage is [target, [[row, col], ...]] with 1-based cells

    problem = pulp.LpProblem("kenken", pulp.LpMinimize)  # satisfaction: no objective

    # put[r][c][v] = 1 if the cell in row r, column c holds the digit v + 1.
    # A cell holds exactly one digit, and x reads that digit back.
    put = pulp.LpVariable.dicts("put", (range(n), range(n), range(n)), cat="Binary")
    x = [[pulp.LpVariable(f"x_{r}_{c}", 1, n, cat="Integer") for c in range(n)]
         for r in range(n)]
    for r in range(n):
        for c in range(n):
            problem += pulp.lpSum(put[r][c][v] for v in range(n)) == 1
            problem += x[r][c] == pulp.lpSum((v + 1) * put[r][c][v] for v in range(n))

    for v in range(n):
        # each row holds the digit v + 1 once
        for r in range(n):
            problem += pulp.lpSum(put[r][c][v] for c in range(n)) == 1
        # each column holds the digit v + 1 once
        for c in range(n):
            problem += pulp.lpSum(put[r][c][v] for r in range(n)) == 1

    # Primes up to n. A digit 1..n only has these prime factors, so a product of digits
    # equals a target exactly when every prime occurs equally often on both sides.
    primes = [p for p in range(2, n + 1) if all(p % q for q in range(2, p))]

    def exponent(p, number):
        """how many times the prime p divides number"""
        count = 0
        while number % p == 0:
            number //= p
            count += 1
        return count

    for k, (target, cells) in enumerate(cages):
        cells = [(r - 1, c - 1) for r, c in cells]  # to 0-based

        if len(cells) == 1:
            # a single cell: its sum and its product are both the digit, which is the target
            (r, c), = cells
            problem += x[r][c] == target

        elif len(cells) == 2:
            # Two cells a, b: the pair of digits must satisfy one of the six relations
            # a + b, a * b, a - b, b - a, a / b or b / a equals the target. The allowed
            # digit pairs are listed, and pair[(u, v)] = 1 if a is u and b is v. The pair is
            # tied to the two cells by its sums, which needs no big-M. pair is continuous:
            # once put is 0/1 the sums leave a single pair with value 1.
            (ra, ca), (rb, cb) = cells
            allowed = [(u, v) for u in range(1, n + 1) for v in range(1, n + 1)
                       if u + v == target or u * v == target or u * target == v
                       or v * target == u or u - v == target or v - u == target]
            pair = {uv: pulp.LpVariable(f"pair_{k}_{uv[0]}_{uv[1]}", 0, 1) for uv in allowed}
            for u in range(1, n + 1):
                # a holds u: exactly one allowed pair starts with u (none if a is not u)
                problem += pulp.lpSum(pair[(u, v)] for v in range(1, n + 1)
                                      if (u, v) in pair) == put[ra][ca][u - 1]
            for v in range(1, n + 1):
                # b holds v: exactly one allowed pair ends with v (none if b is not v)
                problem += pulp.lpSum(pair[(u, v)] for u in range(1, n + 1)
                                      if (u, v) in pair) == put[rb][cb][v - 1]

        else:
            # Three or more cells: the digits add up to the target or multiply to it.
            # by_sum / by_product = 1 if the cage is satisfied by that operation; at least
            # one holds, and an operation that is not chosen leaves its constraints slack.
            size = len(cells)
            by_sum = pulp.LpVariable(f"by_sum_{k}", cat="Binary")
            by_product = pulp.LpVariable(f"by_product_{k}", cat="Binary")
            problem += by_sum + by_product >= 1

            # sum of the digits = target; the sum lies in size..size * n, so the slack
            # needed when the constraint is off is the distance from the target to those ends
            total = pulp.lpSum(x[r][c] for r, c in cells)
            problem += total - target <= (size * n - target) * (1 - by_sum)
            problem += total - target >= (size - target) * (1 - by_sum)

            # product of the digits = target: for every prime p, the exponents of p in the
            # digits add up to the exponent of p in the target. A target with a prime factor
            # above n cannot be a product of digits.
            rest = target
            for p in primes:
                while rest % p == 0:
                    rest //= p
            if rest != 1:
                problem += by_product == 0
            else:
                for p in primes:
                    # exponent of p in the digit v + 1, summed over the cage's cells
                    exp_total = pulp.lpSum(exponent(p, v + 1) * put[r][c][v]
                                           for r, c in cells for v in range(n))
                    wanted = exponent(p, target)
                    most = size * max(exponent(p, v) for v in range(1, n + 1))
                    problem += exp_total - wanted <= (most - wanted) * (1 - by_product)
                    problem += exp_total - wanted >= (0 - wanted) * (1 - by_product)

    return problem, {"x": x}
