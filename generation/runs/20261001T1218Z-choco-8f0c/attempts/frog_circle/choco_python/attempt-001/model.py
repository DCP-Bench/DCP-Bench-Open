# Frog circle: arrange the cards 1..n in a circle so that a frog that starts on card 1 and
# jumps from card k to the card k places clockwise lands on every card.
from pychoco.model import Model


def build(instance):
    n = instance["n"]  # number of cards

    model = Model()

    # x[p] = the card at position p of the circle (positions are 0..n-1 clockwise)
    x = [model.intvar(1, n, name=f"x_{p}") for p in range(n)]
    # pos[i] = the position of the frog after i jumps
    pos = [model.intvar(0, n - 1, name=f"pos_{i}") for i in range(n)]
    # visited[i] = the card the frog stands on after i jumps
    visited = [model.intvar(1, n, name=f"visited_{i}") for i in range(n)]

    # each card is used once, the frog visits every position once and every card once
    model.all_different(x).post()
    model.all_different(pos).post()
    model.all_different(visited).post()

    # the frog starts on card 1, which is at position 0
    model.arithm(x[0], "=", 1).post()
    model.arithm(pos[0], "=", 0).post()
    model.arithm(visited[0], "=", 1).post()

    for i in range(1, n):
        # the next position is the previous position plus the card it stands on, around the circle:
        # pos[i] = (pos[i - 1] + x[pos[i - 1]]) mod n
        card_before = model.intvar(1, n, name=f"card_before_{i}")  # x[pos[i - 1]]
        model.element(card_before, x, pos[i - 1]).post()
        unwrapped = model.intvar(1, 2 * n - 1, name=f"unwrapped_{i}")  # pos[i - 1] + card, before the mod
        model.arithm(pos[i - 1], "+", card_before, "=", unwrapped).post()
        model.mod(unwrapped, n, pos[i]).post()
        # the card visited in this step is the card at the new position
        model.element(visited[i], x, pos[i]).post()

    return model, {"x": x}
