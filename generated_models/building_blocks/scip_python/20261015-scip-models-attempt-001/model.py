# Building blocks: place each letter of the alphabet on one of the blocks so that
# every block shows exactly num_sides letters and every word can be spelled.
from pyscipopt import Model, quicksum


def build(instance):
    alphabet = instance["alphabet"]
    num_blocks = instance["num_blocks"]
    num_sides = instance["num_sides"]
    num_letters = instance["num_letters"]
    words = instance["words_str"]
    model = Model()

    # x[l, b] = 1 if letter l of the alphabet is on block b
    x = {(l, b): model.addVar(name=f"x_{l}_{b}", vtype="B")
         for l in range(num_letters) for b in range(num_blocks)}

    # each letter is on exactly one block
    for l in range(num_letters):
        model.addCons(quicksum(x[l, b] for b in range(num_blocks)) == 1)

    # each block has exactly num_sides letters on its sides
    for b in range(num_blocks):
        model.addCons(quicksum(x[l, b] for l in range(num_letters)) == num_sides)

    # a word is spelled by taking its letters from different blocks, one letter per block
    for word in words:
        idx = [alphabet.index(ch) for ch in word]
        for b in range(num_blocks):
            model.addCons(quicksum(x[l, b] for l in idx) <= 1)

    # the output gives the block of each letter
    dice = [quicksum(b * x[l, b] for b in range(num_blocks)) for l in range(num_letters)]
    return model, {"dice": dice}
