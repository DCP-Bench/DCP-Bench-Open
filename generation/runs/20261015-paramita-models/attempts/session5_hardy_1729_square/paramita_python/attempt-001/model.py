"""Four different numbers from 1 to 100 with a^2 + b^2 = c^2 + d^2 (Hardy-Ramanujan 1729 square); print (a, b, c, d)."""
from paramita.modelling import Bool, If

LOW, HIGH = 1, 100
BITS = 14  # 100 * 100 = 10000 < 2**14, so 14 bits hold every square
NAMES = ["a", "b", "c", "d"]
VALUES = range(LOW, HIGH + 1)


def build(instance):
    # The problem fixes the domain 1..100 and has no instance data.
    # Each number is one-hot over its values; its square is held in binary bits.
    value = {x: {v: Bool(f"{x}_is_{v}") for v in VALUES} for x in NAMES}
    square = {x: [Bool(f"{x}_square_bit_{k}") for k in range(BITS)] for x in NAMES}
    cons = []

    # each of a, b, c, d is one number between 1 and 100
    for x in NAMES:
        cons.append(sum(value[x].values()) == 1)

    # the four numbers are different: each value is used by at most one of them
    for v in VALUES:
        cons.append(sum(value[x][v] for x in NAMES) <= 1)

    # the square of each number, bit by bit: if the number is v, its square bits spell v*v
    for x in NAMES:
        for v in VALUES:
            for k in range(BITS):
                bit = (v * v >> k) & 1
                cons.append(If(value[x][v], square[x][k] if bit else ~square[x][k]))

    # a^2 + b^2 = c^2 + d^2
    def square_of(x):
        return sum(2**k * square[x][k] for k in range(BITS))

    cons.append(square_of("a") + square_of("b") == square_of("c") + square_of("d"))

    # print (a, b, c, d)
    outputs = {x: sum(v * value[x][v] for v in VALUES) for x in NAMES}
    return cons, outputs
