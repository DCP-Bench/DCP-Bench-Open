from ortools.sat.python import cp_model


def build(instance):
    """Building blocks: work out which letters sit on which alphabet block,
    given a list of words each block set must be able to spell.
    """
    num_blocks = instance["num_blocks"]
    num_sides = instance["num_sides"]
    num_letters = instance["num_letters"]
    alphabet = instance["alphabet"]
    words_str = instance["words_str"]

    letter_map = {letter: i for i, letter in enumerate(alphabet)}
    words = [[letter_map[c] for c in word] for word in words_str]

    model = cp_model.CpModel()
    dice = [model.new_int_var(0, num_blocks - 1, f"d{i}") for i in range(num_letters)]

    # The letters of a word must come off different blocks.
    for word in words:
        model.add_all_different([dice[letter] for letter in word])

    # Every block carries exactly num_sides letters.
    on_block = [[model.new_bool_var(f"on{i}_{b}") for b in range(num_blocks)]
                for i in range(num_letters)]
    for i in range(num_letters):
        for b in range(num_blocks):
            model.add(dice[i] == b).only_enforce_if(on_block[i][b])
            model.add(dice[i] != b).only_enforce_if(~on_block[i][b])
    for b in range(num_blocks):
        model.add(sum(on_block[i][b] for i in range(num_letters)) == num_sides)

    return model, {"dice": dice}
