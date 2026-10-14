# The card game Set: among the cards on the table find three that form a set,
# that is, for each of the four features (number, fill, colour, shape) the three
# cards either all show the same value or all show different values.
from pychoco.model import Model


def build(instance):
    cards = instance["cards_data"]  # each card is [number, fill, colour, shape]
    n_cards = len(cards)
    n_features = 4

    model = Model()

    # winning_cards = the indices of the three chosen cards, all different
    winning_cards = [model.intvar(0, n_cards - 1, name=f"winning_{k}") for k in range(3)]
    model.all_different(winning_cards).post()

    for f in range(n_features):
        feature_of_card = [card[f] for card in cards]
        lo, hi = min(feature_of_card), max(feature_of_card)
        # the value of feature f on each chosen card, read from the table of cards
        shown = []
        for k in range(3):
            value = model.intvar(lo, hi, name=f"feature_{f}_card_{k}")
            model.element(value, feature_of_card, winning_cards[k]).post()
            shown.append(value)
        # the three values are either all equal or all different
        model.or_([model.all_equal(shown), model.all_different(shown)]).post()

    return model, {"winning_cards": winning_cards}
