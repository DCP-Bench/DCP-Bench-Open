# Ages of the three sons of an old man, found by the mathematician from three clues:
# the product of the ages is 36; the sum equals the number of windows of a building
# (so the sum is one that more than one product-36 triple has); the oldest son has
# blue eyes (so the oldest son is identified by age, i.e. the oldest age is unique).
from pyscipopt import Model, quicksum

# the triples of ages (oldest first) whose product is 36, with 36 = 2^2 * 3^2
CANDIDATES = [
    (36, 1, 1),
    (18, 2, 1),
    (12, 3, 1),
    (9, 4, 1),
    (6, 6, 1),
    (9, 2, 2),
    (6, 3, 2),
    (4, 3, 3),
]


def build(instance):
    model = Model()

    # one binary per candidate triple: it is the sons' ages
    pick = [model.addVar(name=f"pick_{k}", vtype="B") for k in range(len(CANDIDATES))]
    # the ages of the sons, oldest first (A1 >= A2 >= A3)
    A1 = model.addVar(name="A1", vtype="I", lb=1, ub=36)
    A2 = model.addVar(name="A2", vtype="I", lb=1, ub=36)
    A3 = model.addVar(name="A3", vtype="I", lb=1, ub=36)

    # exactly one candidate triple is the answer
    model.addCons(quicksum(pick) == 1, name="one_triple")
    # the ages are the chosen triple
    model.addCons(A1 == quicksum(t[0] * pick[k] for k, t in enumerate(CANDIDATES)), name="age_oldest")
    model.addCons(A2 == quicksum(t[1] * pick[k] for k, t in enumerate(CANDIDATES)), name="age_middle")
    model.addCons(A3 == quicksum(t[2] * pick[k] for k, t in enumerate(CANDIDATES)), name="age_youngest")

    # the sum of the ages equals the number of windows, and that sum is one the
    # mathematician could not tell apart from another product-36 triple: count the
    # candidate triples with the same sum as the answer
    sums = [sum(t) for t in CANDIDATES]
    shared = [sum(1 for s in sums if s == sums[k]) for k in range(len(CANDIDATES))]
    # the answer must share its sum with at least one other triple ("I need more information")
    model.addCons(quicksum(shared[k] * pick[k] for k in range(len(CANDIDATES))) >= 2,
                  name="sum_not_unique")

    # the oldest son has blue eyes and the mathematician now knows the answer: among the
    # triples with the answer's sum, exactly one has a unique oldest age. The answer
    # must be that triple.
    unique_oldest = [t[0] > t[1] for t in CANDIDATES]
    for k, t in enumerate(CANDIDATES):
        if not unique_oldest[k]:
            # the oldest son is not identified by age, so this triple cannot be the answer
            model.addCons(pick[k] == 0, name=f"oldest_tied_{k}")
    same_sum_unique = [sum(1 for j, u in enumerate(CANDIDATES)
                           if sums[j] == sums[k] and unique_oldest[j])
                       for k in range(len(CANDIDATES))]
    model.addCons(quicksum(same_sum_unique[k] * pick[k] for k in range(len(CANDIDATES))) == 1,
                  name="oldest_identifies_answer")

    # outputs: the sons' ages, oldest first (satisfaction problem, no objective)
    return model, {"A1": A1, "A2": A2, "A3": A3}
