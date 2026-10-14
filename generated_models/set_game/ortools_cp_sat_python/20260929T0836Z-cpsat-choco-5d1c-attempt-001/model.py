# The card game Set: among the cards on the table find three that form a set,
# that is, for each of the four features (number, fill, colour, shape) the three
# cards either all show the same value or all show different values.
from ortools.sat.python import cp_model


def build(instance):
    cards = instance["cards_data"]  # each card is [number, fill, colour, shape]
    n_cards = len(cards)
    n_features = 4

    model = cp_model.CpModel()

    # winning_cards = the indices of the three chosen cards, all different
    winning_cards = [model.new_int_var(0, n_cards - 1, f"winning_{k}") for k in range(3)]
    model.add_all_different(winning_cards)

    for f in range(n_features):
        feature_of_card = [card[f] for card in cards]
        lo, hi = min(feature_of_card), max(feature_of_card)
        # the value of feature f on each chosen card, read from the table of cards
        shown = []
        for k in range(3):
            value = model.new_int_var(lo, hi, f"feature_{f}_card_{k}")
            model.add_element(winning_cards[k], feature_of_card, value)
            shown.append(value)
        # the three values are either all equal or all different
        all_equal = model.new_bool_var(f"all_equal_{f}")
        model.add(shown[0] == shown[1]).only_enforce_if(all_equal)
        model.add(shown[1] == shown[2]).only_enforce_if(all_equal)
        model.add(shown[0] != shown[1]).only_enforce_if(all_equal.negated())
        model.add(shown[1] != shown[2]).only_enforce_if(all_equal.negated())
        model.add(shown[0] != shown[2]).only_enforce_if(all_equal.negated())

    return model, {"winning_cards": winning_cards}
