# Farmer and cows: a farmer has num_cows cows, cow i (numbered 1..num_cows)
# gives i units of milk. He distributes the cows to num_sons sons so that son s
# gets cows_per_son[s] cows and every son gets the same total quantity of milk.
# Encoding: one-hot Booleans x[i][s] (cow i goes to son s). Milk per son is a
# weighted sum of the cow numbers, with the cow number as the weight. The
# cow counts and the son count come from the instance.
from paramita.modelling import Bool


def build(instance):
    num_cows = instance["num_cows"]
    num_sons = instance["num_sons"]
    cows_per_son = instance["cows_per_son"]
    cons = []

    # x[i][s] = 1 if cow i (numbered i + 1) goes to son s.
    x = [[Bool(f"cow_{i}_son_{s}") for s in range(num_sons)] for i in range(num_cows)]

    # Each cow goes to exactly one son.
    for i in range(num_cows):
        cons.append(sum(x[i]) == 1)

    # Each son receives the number of cows given by the distribution.
    for s in range(num_sons):
        cons.append(sum(x[i][s] for i in range(num_cows)) == cows_per_son[s])

    # Each cow gives a quantity of milk equal to its number (i + 1). The total
    # milk of every son is the same, so every son's milk equals the milk of son 0.
    milk = [sum((i + 1) * x[i][s] for i in range(num_cows)) for s in range(num_sons)]
    for s in range(1, num_sons):
        cons.append(milk[s] == milk[0])

    # Output: the son (0-based) of each cow, in cow order.
    cow_assignments = [sum(s * x[i][s] for s in range(num_sons)) for i in range(num_cows)]

    return cons, {"cow_assignments": cow_assignments}
