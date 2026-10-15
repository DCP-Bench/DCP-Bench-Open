# de Bruijn sequence B(base, n): a cyclic sequence of length base^n over the
# alphabet 0..base-1 in which every length-n string occurs exactly once as a
# (cyclic) substring. Letters are one-hot per position, because they are
# matched against the words.
from functools import reduce

from paramita.modelling import Bool, Iff


def build(instance):
    base, n = instance["base"], instance["n"]
    length = base ** n  # the sequence length equals the number of words

    # one-hot letter per position: x[p][a] = 1 if position p holds letter a
    x = [[Bool(f"x_{p}_{a}") for a in range(base)] for p in range(length)]
    cons = []

    # each position holds exactly one letter
    cons += [sum(x[p]) == 1 for p in range(length)]

    # the window starting at position i covers the n letters i, i+1, ... (cyclic)
    # wb[i][v] = 1 if the window at position i reads the word v
    # (word v written in base-ary digits, most significant first)
    wb = [[Bool(f"w_{i}_{v}") for v in range(length)] for i in range(length)]
    for i in range(length):
        for v in range(length):
            digits = [(v // base ** (n - 1 - j)) % base for j in range(n)]
            lits = [x[(i + j) % length][digits[j]] for j in range(n)]
            cons.append(Iff(wb[i][v], reduce(lambda a, b: a & b, lits)))

    # each window reads exactly one word
    cons += [sum(wb[i]) == 1 for i in range(length)]

    # every possible length-n string occurs exactly once as a cyclic substring
    cons += [sum(wb[i][v] for i in range(length)) == 1 for v in range(length)]

    # the sequence, letter by letter
    sequence = [sum(a * x[p][a] for a in range(base)) for p in range(length)]

    return cons, {"de_bruijn": sequence}
