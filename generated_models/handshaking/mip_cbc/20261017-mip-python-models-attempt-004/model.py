# Handshaking (Halmos): Hilary and Jocelyn are married and invite some couples
# for dinner. Everyone shakes hands with each other, except themselves and their
# spouse. Jocelyn then asks each person, except herself, how many hands they shook,
# and all the answers are different. Output hil: the number of hands Hilary shook.
import mip


def build(instance):
    # num_couples counts the invited couples; the hosts' couple is added to them.
    total_couples = instance["num_couples"] + 1
    persons = 2 * total_couples
    # Persons 2k and 2k+1 are a couple, so person 0 is Hilary and person 1 is Jocelyn.
    max_hands = persons - 2

    def spouse(i):
        return i ^ 1

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")
    model.verbose = 0

    # Nobody shakes hands with him or herself or with his or her spouse.
    # Every other pair of persons has one binary: 1 if they shake hands.
    shake = {}
    for i in range(persons):
        for j in range(i + 1, persons):
            if j != spouse(i):
                shake[i, j] = model.add_var(f"shake_{i}_{j}", var_type=mip.BINARY)

    def handshake(i, j):
        return shake[min(i, j), max(i, j)]

    # The hands count of each person is the number of handshakes that person takes part in.
    hands = []
    for i in range(persons):
        h = model.add_var(f"hands_{i}", lb=0, ub=max_hands, var_type=mip.INTEGER)
        model.add_constr(h == mip.xsum(handshake(i, j) for j in range(persons) if j != i and j != spouse(i)))
        hands.append(h)

    # All the answers are different: each person except Jocelyn gives a different hands count.
    # One-hot binaries pick the count of each person; each count value is used at most once.
    answerers = [i for i in range(persons) if i != 1]
    pick = {}
    for i in answerers:
        for v in range(max_hands + 1):
            pick[i, v] = model.add_var(f"pick_{i}_{v}", var_type=mip.BINARY)
        model.add_constr(mip.xsum(pick[i, v] for v in range(max_hands + 1)) == 1)
        model.add_constr(hands[i] == mip.xsum(v * pick[i, v] for v in range(max_hands + 1)))
    # There are as many answerers as values 0..max_hands, so each value is taken exactly once.
    for v in range(max_hands + 1):
        model.add_constr(mip.xsum(pick[i, v] for i in answerers) == 1)

    # Each invited couple: the two spouses' hand counts add up to persons - 2.
    # Each answer is a value of 0..persons-2, so the spouse of the person with
    # the count k has the count persons - 2 - k (the couples pair up the values).
    for k in range(1, instance["num_couples"] + 1):
        model.add_constr(hands[2 * k] + hands[2 * k + 1] == max_hands)

    return model, {"hil": hands[0]}
