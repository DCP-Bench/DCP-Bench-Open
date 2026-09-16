import pulp


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

    problem = pulp.LpProblem("blocks", pulp.LpMinimize)
    on = pulp.LpVariable.dicts("on", (range(num_letters), range(num_blocks)),
                               cat="Binary")
    dice = [pulp.LpVariable(f"d{i}", 0, num_blocks - 1, cat="Integer")
            for i in range(num_letters)]
    for i in range(num_letters):
        problem += pulp.lpSum(on[i][b] for b in range(num_blocks)) == 1
        problem += dice[i] == pulp.lpSum(b * on[i][b] for b in range(num_blocks))

    # Every block carries exactly num_sides letters.
    for b in range(num_blocks):
        problem += pulp.lpSum(on[i][b] for i in range(num_letters)) == num_sides

    # The letters of a word must come off different blocks.
    for word in words:
        for b in range(num_blocks):
            problem += pulp.lpSum(on[letter][b] for letter in word) <= 1

    return problem, {"dice": dice}
