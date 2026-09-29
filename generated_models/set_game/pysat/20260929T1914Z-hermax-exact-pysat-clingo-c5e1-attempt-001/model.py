# The card game Set: among the cards on the table find three that form a set,
# that is, for each of the four features (number, fill, colour, shape) the three
# cards either all show the same value or all show different values.
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    cards = instance["cards_data"]  # each card is [number, fill, colour, shape]
    n_cards = len(cards)
    n_features = 4

    pool = IDPool()
    # winning_cards = the indices of the three chosen cards
    winning_cards = [Integer(f"winning_{k}", 0, n_cards - 1, vpool=pool) for k in range(3)]
    engine = IntegerEngine(vars=winning_cards, vpool=pool)
    # the three chosen cards are different
    engine.add_alldifferent(winning_cards)
    cnf = engine.clausify()

    # For each of the four features: if two of the chosen cards share a value, the
    # third one shares it too. Forbid every choice where cards c1 and c2 (at
    # positions a and b) share a value and the card c3 at the remaining position
    # has another one.
    for f in range(n_features):
        for a, b, c in ((0, 1, 2), (0, 2, 1), (1, 2, 0)):
            for c1 in range(n_cards):
                for c2 in range(n_cards):
                    if cards[c1][f] != cards[c2][f]:
                        continue
                    for c3 in range(n_cards):
                        if cards[c3][f] != cards[c1][f]:
                            cnf.append([-winning_cards[a].equals(c1), -winning_cards[b].equals(c2),
                                        -winning_cards[c].equals(c3)])

    return cnf, {"winning_cards": winning_cards}
