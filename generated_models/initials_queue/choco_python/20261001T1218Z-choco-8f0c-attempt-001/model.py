# Initials queue: ten people queue, each with initials an alphabetically ordered pair of distinct
# letters from A-E, no two with the same initials, and nobody sharing a letter with the person in
# front. BE is first, CD second and BD last. Find the queue.
from pychoco.model import Model

# The puzzle has no instance data; the queue length, the letters and the three known places are
# its statement.
N = 10
A, B, C, D, E = range(5)
KNOWN = {0: (B, E), 1: (C, D), N - 1: (B, D)}


def build(instance):
    del instance  # the puzzle carries no instance data

    model = Model()

    # queue[i] = the two initials of person i, front of the queue first
    queue = [[model.intvar(A, E, name=f"queue_{i}_{k}") for k in range(2)] for i in range(N)]

    # Initials are an alphabetically ordered pair of distinct letters; pair_id[i] numbers the pair
    # so that "no two people have the same initials" is "the pair numbers are all different".
    pairs = [(x, y) for x in range(A, E + 1) for y in range(x + 1, E + 1)]
    rows = [(x, y, idx) for idx, (x, y) in enumerate(pairs)]
    pair_id = []
    for i in range(N):
        pid = model.intvar(0, len(pairs) - 1, name=f"pair_{i}")
        model.table(queue[i] + [pid], rows).post()
        pair_id.append(pid)
    model.all_different(pair_id).post()

    # No-one shares a letter with the person in front of them.
    for i in range(N - 1):
        for x in queue[i]:
            for y in queue[i + 1]:
                model.arithm(x, "!=", y).post()

    # BE is at the front, CD right behind, and BD at the end.
    for i, (x, y) in KNOWN.items():
        model.arithm(queue[i][0], "=", x).post()
        model.arithm(queue[i][1], "=", y).post()

    return model, {"queue": queue}
