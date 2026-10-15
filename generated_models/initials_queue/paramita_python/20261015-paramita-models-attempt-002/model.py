# Queue of 10 people for a Maths lecture, each with a distinct pair of initials from A..E; find the queue.
from paramita.modelling import Bool

# Letters A..E are the integers 0..4. The 10 alphabetically ordered pairs of distinct letters.
PAIRS = [(a, b) for a in range(5) for b in range(a + 1, 5)]


def pair_index(letters):
    return PAIRS.index(tuple(letters))


def build(instance):
    # The problem has no instance data: the queue is 10 people, the letter set is fixed at 5.
    n = 10
    k = len(PAIRS)

    # One-hot encoding: p[i][j] is true when the person at queue place i has initials PAIRS[j].
    p = [[Bool(f"p_{i}_{j}") for j in range(k)] for i in range(n)]

    subject_to = []
    # Each person has exactly one pair of initials from the first five letters.
    subject_to += [sum(p[i]) == 1 for i in range(n)]
    # None of the people had the same initials as any other: each of the 10 pairs is used exactly once.
    subject_to += [sum(p[i][j] for i in range(n)) == 1 for j in range(k)]
    # No-one shared a letter with the person in front of them.
    for i in range(n - 1):
        for j in range(k):
            for l in range(k):
                if set(PAIRS[j]) & set(PAIRS[l]):
                    subject_to.append(~(p[i][j] & p[i + 1][l]))
    # BE was at the front of the queue.
    subject_to.append(p[0][pair_index((1, 4))])
    # with CD right behind.
    subject_to.append(p[1][pair_index((2, 3))])
    # BD was right at the end of the queue.
    subject_to.append(p[n - 1][pair_index((1, 3))])

    # Output: the letters of each queue place as integers 0..4.
    queue = [
        [sum(PAIRS[j][0] * p[i][j] for j in range(k)),
         sum(PAIRS[j][1] * p[i][j] for j in range(k))]
        for i in range(n)
    ]
    return subject_to, {"queue": queue}
