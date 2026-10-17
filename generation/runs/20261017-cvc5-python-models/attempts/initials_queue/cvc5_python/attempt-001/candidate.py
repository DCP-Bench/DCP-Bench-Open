# Initials queue: ten people in a queue, each with an alphabetically ordered pair of
# distinct letters from A..E (coded 0..4). All initials are different, no two adjacent
# people share a letter, BE is at the front, CD is second, BD is at the end.
import cvc5.pythonic as cz


def build(instance):
    n = 10
    # Each person i has initials (a[i], b[i]) with a[i] < b[i], both in 0..4.
    a = [cz.Int(f"a_{i}") for i in range(n)]
    b = [cz.Int(f"b_{i}") for i in range(n)]
    constraints = []

    # Domain: letters are A..E, coded 0..4.
    for i in range(n):
        constraints += [a[i] >= 0, a[i] <= 4, b[i] >= 0, b[i] <= 4]

    # An alphabetically ordered pair of distinct letters.
    # Each initials pair is an alphabetically ordered pair of distinct letters.
    for i in range(n):
        constraints.append(a[i] < b[i])

    # None of the people had the same initials as any other person.
    # All initials are different.
    codes = [5 * a[i] + b[i] for i in range(n)]
    constraints.append(cz.Distinct(codes))

    # No-one shared a letter with the person in front of them.
    # Adjacent people share no letter.
    for i in range(n - 1):
        constraints += [
            a[i] != a[i + 1],
            a[i] != b[i + 1],
            b[i] != a[i + 1],
            b[i] != b[i + 1],
        ]

    # Mathematician BE was at the front of the queue with CD right behind.
    # BE is (1, 4), CD is (2, 3) in 0-based letter codes.
    constraints += [a[0] == 1, b[0] == 4]
    constraints += [a[1] == 2, b[1] == 3]

    # BD was right at the end of the queue.
    constraints += [a[n - 1] == 1, b[n - 1] == 3]

    queue = [[a[i], b[i]] for i in range(n)]
    return constraints, {"queue": queue}
