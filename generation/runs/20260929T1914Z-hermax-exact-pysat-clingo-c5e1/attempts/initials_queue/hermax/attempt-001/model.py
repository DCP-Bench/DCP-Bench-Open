# Initials queue: the ten people in a queue have as initials the ten different
# alphabetically ordered pairs of distinct letters from A-E, no one shares a
# letter with the person in front, BE is first, CD second and BD last.
from itertools import combinations

from hermax.model import Model


def build(instance):
    n = 10  # people in the queue
    letters = 5  # the initials are from A..E, coded 0..4
    # the ten possible initials, in alphabetical order, and the number of each
    pairs = list(combinations(range(letters), 2))
    number = {pair: idx for idx, pair in enumerate(pairs)}

    m = Model()
    # queue[i] = the two letters of the i-th person, counted from the front
    queue = m.int_matrix("queue", n, 2, 0, letters - 1)
    # initials[i] = the number of the initials of the i-th person
    initials = m.int_vector("initials", n, 0, len(pairs) - 1)

    # the letters of a person are an alphabetically ordered pair of distinct letters
    for i in range(n):
        m &= m.vector([queue[i][0], queue[i][1], initials[i]]).is_in(
            [(a, b, number[(a, b)]) for a, b in pairs])

    # nobody has the same initials as anybody else
    m &= m.vector([initials[i] for i in range(n)]).all_different()

    # nobody shares a letter with the person in front: consecutive people have
    # initials with no letter in common
    apart = [(number[p], number[q]) for p in pairs for q in pairs if not set(p) & set(q)]
    for i in range(n - 1):
        m &= m.vector([initials[i], initials[i + 1]]).is_in(apart)

    # BE is at the front, CD right behind, BD at the end
    m &= (initials[0] == number[(1, 4)])
    m &= (initials[1] == number[(2, 3)])
    m &= (initials[n - 1] == number[(1, 3)])

    return m, {"queue": queue}
