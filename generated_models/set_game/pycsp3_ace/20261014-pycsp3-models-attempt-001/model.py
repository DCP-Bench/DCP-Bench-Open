from itertools import product

from pycsp3 import *

# Find three different cards that form a set: for each of the four features, the
# three cards show that feature either all the same or all different.

cards = data.cards_data  # cards[i] holds the four feature values of card i, each 1 to 3
n_cards = len(cards)
n_features = 4

# winning_cards[k] is the index of the k-th card of the set
winning_cards = VarArray(size=3, dom=range(n_cards))

# value[k][f] is the value of feature f on the k-th card of the set
value = VarArray(size=[3, n_features], dom=range(1, 4))

# the allowed triples of values for one feature: all the same, or all different
same_or_different = [t for t in product(range(1, 4), repeat=3)
                     if t[0] == t[1] == t[2] or len(set(t)) == 3]

satisfy(
    # the three cards of the set are different cards
    AllDifferent(winning_cards),

    # the value of each feature on a card is the value the card shows
    [Table(scope=[winning_cards[k], value[k][f]],
           supports=[(i, cards[i][f]) for i in range(n_cards)])
     for k in range(3) for f in range(n_features)],

    # for each feature the three cards are all the same or all different
    [Table(scope=[value[0][f], value[1][f], value[2][f]], supports=same_or_different)
     for f in range(n_features)],
)
