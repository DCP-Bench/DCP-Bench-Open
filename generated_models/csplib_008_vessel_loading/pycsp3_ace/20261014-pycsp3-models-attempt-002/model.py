from pycsp3 import *

# Vessel loading: place all containers on the deck, without overlap and with the required separations.
# The deck width runs along x and the deck length along y. Coordinates start at 0.
# left and right are the x-edges of a container (right edge excluded), bottom and top its y-edges
# (top edge excluded, so top lies above bottom). Each container may be turned by 90 degrees.
n = data.n_containers
W = data.deck_width
L = data.deck_length

left = VarArray(size=n, dom=range(W + 1), id="left")
right = VarArray(size=n, dom=range(W + 1), id="right")
bottom = VarArray(size=n, dom=range(L + 1), id="bottom")
top = VarArray(size=n, dom=range(L + 1), id="top")

# sx[i], sy[i]: the extent of container i along the deck width and along the deck length
dims = set(data.width) | set(data.length)
sx = VarArray(size=n, dom=dims, id="sx")
sy = VarArray(size=n, dom=dims, id="sy")

# minimum distance required between container i and container j, from their classes
# (classes are numbered from 1, the separation matrix from 0)
min_gap = [[data.separation[data.classes[i] - 1][data.classes[j] - 1] for j in range(n)] for i in range(n)]

satisfy(
    # each container is parallel to the deck sides, with its width along the deck width or turned by 90 degrees
    [(sx[i], sy[i]) in {(data.width[i], data.length[i]), (data.length[i], data.width[i])} for i in range(n)],
    # the right edge of each container is its left edge plus its extent along the deck width
    [right[i] == left[i] + sx[i] for i in range(n)],
    # the top edge of each container is its bottom edge plus its extent along the deck length
    [top[i] == bottom[i] + sy[i] for i in range(n)],
    # every container lies on the deck
    [right[i] <= W for i in range(n)],
    [top[i] <= L for i in range(n)],
)

satisfy(
    # no two containers overlap, and containers of classes with a separation are apart by that minimum distance,
    # either along the deck or across it
    [Or(right[i] + min_gap[i][j] <= left[j],
        right[j] + min_gap[i][j] <= left[i],
        top[i] + min_gap[i][j] <= bottom[j],
        top[j] + min_gap[i][j] <= bottom[i])
     for i in range(n) for j in range(i + 1, n)],
)
