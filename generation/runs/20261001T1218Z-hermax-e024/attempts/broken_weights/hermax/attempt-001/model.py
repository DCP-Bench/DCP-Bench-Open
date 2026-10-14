# Broken weights: a measuring weight broke into n pieces of whole-pound
# weights adding up to the original weight. Using the pieces on both pans of a
# balance, every whole weight from 1 up to the original weight can be weighed.
# What are the weights of the pieces?
from hermax.model import Model


def build(instance):
    total = instance["m"]  # the weight before it broke
    n = instance["n"]  # number of pieces

    m = Model()
    # weights[j] = the weight of piece j, a whole number of pounds between 1 and total
    weights = m.int_vector("weights", n, 1, total)

    # the pieces add up to the original weight
    m &= (sum(weights[j] for j in range(n)) == total)

    # Every weight 1..total can be weighed. A piece goes on the same pan as the
    # object, on the other pan, or stays off, so a weighable weight is a signed
    # sum of some of the pieces. Instead of giving every target its own signs
    # (which multiplies a variable weight by a variable sign), track which
    # differences can be made: reach[j][v] is true only if v is the signed sum
    # of some of the first j pieces. v ranges over -total..total, shifted by
    # `total` to index the vector. Only the "true implies justified" direction
    # is posted, which is all that is needed because the targets below demand
    # that entries are true, never false.
    reach = [m.bool_vector(f"reach_{j}", 2 * total + 1) for j in range(n + 1)]
    # with no pieces, only the difference 0 can be made
    for v in range(-total, total + 1):
        if v == 0:
            m &= reach[0][total]
        else:
            m &= ~reach[0][v + total]

    for j in range(n):
        for v in range(-total, total + 1):
            # reach[j+1][v] needs a reason: piece j stays off, or it is used with
            # weight d on one pan or the other starting from a difference that
            # the first j pieces can make
            reasons = [reach[j][v + total]]
            for d in range(1, total + 1):
                sources = []
                if v - d >= -total:
                    sources.append(reach[j][v - d + total])  # piece j adds d
                if v + d <= total:
                    sources.append(reach[j][v + d + total])  # piece j subtracts d
                if not sources:
                    continue
                used = m.bool(f"used_{j}_{v}_{d}")
                m &= (~used | (weights[j] == d))
                clause = ~used
                for source in sources:
                    clause = clause | source
                m &= clause
                reasons.append(used)
            clause = ~reach[j + 1][v + total]
            for reason in reasons:
                clause = clause | reason
            m &= clause

    # every weight from 1 to the original weight can be weighed with all pieces
    for target in range(1, total + 1):
        m &= reach[n][target + total]

    return m, {"weights": weights}
