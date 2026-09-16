import pulp


def build(instance):
    """People in a room: order the arrivals so the ratio of females to males
    never exceeds seven to three. A 1 is a female arrival.
    """
    del instance

    total_people, num_males = 13, 4
    problem = pulp.LpProblem("room", pulp.LpMinimize)
    sequence = [pulp.LpVariable(f"s{i}", cat="Binary")
                for i in range(total_people)]

    problem += pulp.lpSum(sequence) == total_people - num_males
    # Over the first i arrivals, 3F <= 7(i - F), which is 10F <= 7i.
    for i in range(1, total_people):
        problem += 10 * pulp.lpSum(sequence[:i]) <= 7 * i

    return problem, {"sequence": sequence}
