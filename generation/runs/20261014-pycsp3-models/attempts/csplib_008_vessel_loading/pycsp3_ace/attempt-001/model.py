# Vessel loading: place rectangular containers on a rectangular deck without overlap and with the minimum separations between classes.
from pycsp3 import *

deck_width = data.deck_width
deck_length = data.deck_length
n = data.n_containers
width = data.width
length = data.length
classes = data.classes
separation = data.separation

# left[i] and top[i] are the 0-indexed corner of container i; right[i] and bottom[i] are the far edges
left = VarArray(size=n, dom=range(deck_width))
right = VarArray(size=n, dom=range(1, deck_width + 1))
top = VarArray(size=n, dom=range(deck_length))
bottom = VarArray(size=n, dom=range(1, deck_length + 1))

satisfy(
    # each container spans its width along the deck width
    [right[i] == left[i] + width[i] for i in range(n)],
    # each container spans its length along the deck length
    [bottom[i] == top[i] + length[i] for i in range(n)],
)

for i in range(n):
    for j in range(i + 1, n):
        # minimum distance between containers i and j, from the separation table of their classes
        s = separation[classes[i] - 1][classes[j] - 1]
        satisfy(
            # containers must not overlap, and must be the required distance apart, to the left, right, above or below
            Or(
                right[i] + s <= left[j],
                right[j] + s <= left[i],
                bottom[i] + s <= top[j],
                bottom[j] + s <= top[i],
            )
        )
