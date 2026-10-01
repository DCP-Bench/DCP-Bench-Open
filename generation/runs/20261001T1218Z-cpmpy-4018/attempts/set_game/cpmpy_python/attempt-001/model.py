# Set (card game): from the cards on the table, find three cards that form a "set": for each of
# the four features (number, fill, colour, shape) the three cards show it all the same or all
# different.
import cpmpy as cp


def build(instance):
    # cards_data[c] = [number, fill, colour, shape] of card c. The feature values are plain
    # integer codes, so only the cards are needed; the code tables in the instance name the values.
    cards = instance["cards_data"]
    n_cards = len(cards)

    # winning_cards = the indices of the three cards that make up the set
    winning_cards = cp.intvar(0, n_cards - 1, shape=(3,), name="winning_cards")

    model = cp.Model()

    # The three cards are three different cards.
    model += cp.AllDifferent(winning_cards)

    # For each feature, the three chosen cards must show it all the same or all different (no
    # two the same and one different). feature 0 = number, 1 = fill, 2 = colour, 3 = shape.
    for feature in range(4):
        column = cp.cpm_array([card[feature] for card in cards])  # this feature on every card
        shown = [column[winning_cards[k]] for k in range(3)]       # this feature on the chosen cards
        model += cp.AllEqual(shown) | cp.AllDifferent(shown)

    return model, {"winning_cards": winning_cards}
