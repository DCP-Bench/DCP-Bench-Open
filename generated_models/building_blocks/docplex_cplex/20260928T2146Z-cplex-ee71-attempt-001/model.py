"""Building blocks: put the letters on the blocks, a fixed number per block, so that every word can be spelled with distinct blocks."""
from docplex.mp.model import Model


def build(instance):
    num_blocks, num_sides = instance["num_blocks"], instance["num_sides"]
    alphabet = instance["alphabet"]
    letters = range(instance["num_letters"])
    blocks = range(num_blocks)
    position = {letter: i for i, letter in enumerate(alphabet)}
    words = [[position[c] for c in word] for word in instance["words_str"]]

    model = Model("building_blocks")

    # on[l, b] is 1 when letter l is on block b; every letter is on exactly one block.
    on = model.binary_var_matrix(letters, blocks, name="on")
    for l in letters:
        model.add_constraint(model.sum(on[l, b] for b in blocks) == 1, ctname=f"letter_{l}")

    # The letters of a word are on different blocks, so no block carries two of
    # them. A letter repeated in a word counts twice, as in the reference.
    for w, word in enumerate(words):
        for b in blocks:
            model.add_constraint(model.sum(on[l, b] for l in word) <= 1, ctname=f"word_{w}_{b}")

    # Every block has exactly one letter on each of its sides.
    for b in blocks:
        model.add_constraint(model.sum(on[l, b] for l in letters) == num_sides, ctname=f"sides_{b}")

    # The block each letter is on, read back from the assignment.
    return model, {"dice": [model.sum(b * on[l, b] for b in blocks) for l in letters]}
