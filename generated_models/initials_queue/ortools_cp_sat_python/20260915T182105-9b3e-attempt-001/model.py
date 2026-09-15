from ortools.sat.python import cp_model


def build(instance):
    """Initials queue: ten mathematicians whose initials are ordered pairs from
    A..E, all distinct, with no letter shared with the person in front.

    The puzzle states its own queue, so `instance` is unused.  Letters are
    encoded A=0 through E=4.
    """
    del instance

    n = 10
    first, last = 0, 4

    model = cp_model.CpModel()
    queue = [[model.new_int_var(first, last, f"q{i}_{k}") for k in range(2)]
             for i in range(n)]

    # Each person's initials are two distinct letters in alphabetical order.
    for i in range(n):
        model.add(queue[i][0] < queue[i][1])
    # No two people share both initials.  The pair is ordered, so packing it
    # into a single number and demanding those differ says the same thing.
    codes = []
    for i in range(n):
        code = model.new_int_var(0, 5 * 5, f"code{i}")
        model.add(code == queue[i][0] * 5 + queue[i][1])
        codes.append(code)
    model.add_all_different(codes)
    # Nobody shares a letter with the person in front.
    for i in range(n - 1):
        for a in range(2):
            for b in range(2):
                model.add(queue[i][a] != queue[i + 1][b])

    # BE at the front, CD behind, BD at the back.
    model.add(queue[0][0] == 1)
    model.add(queue[0][1] == 4)
    model.add(queue[1][0] == 2)
    model.add(queue[1][1] == 3)
    model.add(queue[n - 1][0] == 1)
    model.add(queue[n - 1][1] == 3)

    return model, {"queue": queue}
