import z3


def build(instance):
    given = instance["isbn_init"]
    n = len(given)
    isbn = [z3.Int(f"d_{i}") for i in range(n)]
    constraints = [d >= 0 for d in isbn] + [d <= 9 for d in isbn]
    # A -1 in the instance marks the digit to find.
    constraints += [isbn[i] == given[i] for i in range(n) if given[i] != -1]
    constraints += [isbn[0] == 9, isbn[1] == 7, z3.Or(isbn[2] == 8, isbn[2] == 9)]
    check = z3.Sum([isbn[i] * (1 if i % 2 == 0 else 3) for i in range(n - 1)])
    constraints.append(isbn[n - 1] == (10 - (check % 10)) % 10)
    return constraints, {"isbn": isbn}
