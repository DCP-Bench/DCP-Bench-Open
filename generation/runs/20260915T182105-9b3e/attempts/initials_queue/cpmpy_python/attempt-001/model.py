import cpmpy as cp


def build(instance):
    """Initials queue: ten mathematicians whose initials are ordered pairs from
    A..E, all distinct, with no letter shared with the person in front.

    The puzzle states its own queue, so `instance` is unused.  Letters are
    encoded A=0 through E=4.
    """
    del instance

    n = 10
    first, last = 0, 4

    queue = cp.intvar(first, last, shape=(n, 2), name="queue")

    model = cp.Model()
    # Each person's initials are two distinct letters in alphabetical order.
    for i in range(n):
        model += queue[i, 0] < queue[i, 1]
    # No two people share both initials.
    for i in range(n):
        for j in range(i + 1, n):
            model += (queue[i, 0] != queue[j, 0]) | (queue[i, 1] != queue[j, 1])
    # Nobody shares a letter with the person in front.
    for i in range(n - 1):
        for a in range(2):
            for b in range(2):
                model += queue[i, a] != queue[i + 1, b]

    # BE at the front, CD behind, BD at the back.
    model += queue[0, 0] == 1
    model += queue[0, 1] == 4
    model += queue[1, 0] == 2
    model += queue[1, 1] == 3
    model += queue[n - 1, 0] == 1
    model += queue[n - 1, 1] == 3

    return model, {"queue": queue}
