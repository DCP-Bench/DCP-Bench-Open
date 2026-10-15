"""Calvin puzzle: completely fill an n by n grid with the numbers 1..n^2 in sequence.

Encoding: one-hot Bools p[r][c][k] (square (r, c) holds number k).
"""
from paramita.modelling import Bool, Or


def build(instance):
    n = instance["n"]
    size = n * n
    nums = range(size)  # index k stands for the number k + 1

    p = [[[Bool(f"p_{r}_{c}_{k}") for k in nums] for c in range(n)] for r in range(n)]

    cons = []

    # completely fill every square: each square holds exactly one number
    for r in range(n):
        for c in range(n):
            cons.append(sum(p[r][c]) == 1)

    # each number is placed once: each number sits in exactly one square
    for k in nums:
        cons.append(sum(p[r][c][k] for r in range(n) for c in range(n)) == 1)

    # Movement Type I: vertically or horizontally, exactly three squares away
    # Movement Type II: diagonally, exactly two squares away
    moves = [(0, 3), (0, -3), (3, 0), (-3, 0),
             (2, 2), (2, -2), (-2, 2), (-2, -2)]

    # the next number is placed by one of the two movement types from the previous one
    for k in nums[:-1]:
        for r in range(n):
            for c in range(n):
                targets = [p[r + dr][c + dc][k + 1]
                           for dr, dc in moves
                           if 0 <= r + dr < n and 0 <= c + dc < n]
                if targets:
                    cons.append(~p[r][c][k] | Or(targets))
                else:
                    cons.append(~p[r][c][k])

    # print the completed grid x: the number in each square
    x = [[sum((k + 1) * p[r][c][k] for k in nums) for c in range(n)] for r in range(n)]
    return cons, {"x": x}
