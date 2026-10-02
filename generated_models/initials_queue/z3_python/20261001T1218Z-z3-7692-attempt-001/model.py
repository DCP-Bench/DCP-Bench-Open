# Initials queue: the first ten people in a queue each have as initials an
# alphabetically ordered pair of distinct letters from A-E. No two people share
# initials, nobody shares a letter with the person in front, BE is first, CD is
# second and BD is last. Find the initials of everyone in the queue.
import z3


def build(instance):
    del instance  # the puzzle states its own queue

    n = 10  # people in the queue
    A, B, C, D, E = range(5)  # letters A..E

    # queue[i] = (first initial, second initial) of person i, front of queue first.
    queue = [[z3.Int(f"queue_{i}_{k}") for k in range(2)] for i in range(n)]

    solver = z3.Solver()
    for pair in queue:
        for letter in pair:
            solver.add(letter >= A, letter <= E)

    # Each person's initials are two distinct letters in alphabetical order.
    for first, second in queue:
        solver.add(first < second)

    # No two people have the same initials.
    for i in range(n):
        for j in range(i + 1, n):
            solver.add(z3.Or(queue[i][0] != queue[j][0], queue[i][1] != queue[j][1]))

    # Nobody shares a letter with the person in front of them.
    for i in range(n - 1):
        for x in queue[i]:
            for y in queue[i + 1]:
                solver.add(x != y)

    # Mathematician BE is at the front of the queue, CD is right behind, and BD
    # is at the very end.
    solver.add(queue[0][0] == B, queue[0][1] == E)
    solver.add(queue[1][0] == C, queue[1][1] == D)
    solver.add(queue[n - 1][0] == B, queue[n - 1][1] == D)

    return solver, {"queue": queue}
