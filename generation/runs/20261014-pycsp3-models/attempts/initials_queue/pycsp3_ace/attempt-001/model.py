from pycsp3 import *

# Ten people in a queue, each with initials made of two distinct letters from A to E
# (0 to 4), written in alphabetical order. No two people have the same initials, and
# no person shares a letter with the person in front of them. BE is at the front,
# CD is right behind, and BD is at the end of the queue.

# queue[k] holds the two letters of the k-th person from the front
queue = VarArray(size=[10, 2], dom=range(5))

satisfy(
    # the two letters of each person are in alphabetical order and distinct
    [queue[k][0] < queue[k][1] for k in range(10)],

    # no two people have the same initials
    AllDifferent([queue[k][0] * 5 + queue[k][1] for k in range(10)]),

    # no person shares a letter with the person in front of them
    [AllDifferent(queue[k] + queue[k + 1]) for k in range(9)],

    # the person at the front of the queue is BE
    [queue[0][0] == 1, queue[0][1] == 4],

    # the person right behind is CD
    [queue[1][0] == 2, queue[1][1] == 3],

    # the person at the end of the queue is BD
    [queue[9][0] == 1, queue[9][1] == 3],
)
