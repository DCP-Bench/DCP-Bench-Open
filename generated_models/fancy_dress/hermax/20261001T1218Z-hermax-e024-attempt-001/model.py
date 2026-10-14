# Fancy dress: Mr Greenguest wants to attend a party where green clothing rules apply or an
# entrance fee is due. Choose which green items to wear (or pay the fee) at least cost.
from hermax.model import Model


def build(instance):
    # The rules and prices are fixed by the problem; the instance carries no data.
    m = Model()
    t = m.bool("t")  # wears a green tie ($10)
    h = m.bool("h")  # wears a green hat ($2)
    r = m.bool("r")  # wears a green shirt (already owned)
    s = m.bool("s")  # wears green socks ($12)
    n = m.bool("n")  # pays the $11 entrance fee instead of following the rules

    # 1. Someone wearing a green tie has to wear a green shirt (or pay the fee).
    m &= (~t | r | n)
    # 2. Green socks or a green shirt only with a green tie or a green hat (or pay the fee).
    m &= (~s | t | h | n)
    m &= (~r | t | h | n)
    # 3. A green shirt, a green hat, or no green socks requires a green tie (or pay the fee).
    m &= (~r | t | n)
    m &= (~h | t | n)
    m &= (s | t | n)

    # Minimise the cost 10 t + 2 h + 12 s + 11 n. A soft clause pays its weight when its
    # literal is false, so each item pays its price through its negation.
    m.obj[10] += ~t
    m.obj[2] += ~h
    m.obj[12] += ~s
    m.obj[11] += ~n

    return m, {"t": t, "h": h, "r": r, "s": s, "n": n}
