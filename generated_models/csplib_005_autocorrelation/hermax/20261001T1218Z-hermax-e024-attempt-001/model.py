# Low autocorrelation binary sequences: choose a sequence of n values, each +1
# or -1, minimising the sum over k = 1..n-1 of the squared periodic
# autocorrelations C_k, where C_k adds up S_i * S_((i+k) mod n) over all i.
from hermax.model import Model


def build(instance):
    n = instance["n"]  # length of the sequence

    m = Model()
    # sequence[i] = the i-th value, -1 or +1 (0 is excluded)
    sequence = m.int_vector("sequence", n, -1, 1)
    for i in range(n):
        m &= (sequence[i] != 0)
    # plus[i] is the literal "sequence[i] is +1"
    plus = [sequence[i] >= 1 for i in range(n)]

    for k in range(1, n):
        # Two values multiply to +1 when they are equal and to -1 when they differ,
        # so C_k = n - 2 * d_k, where d_k is the number of positions i whose value
        # differs from the value k places further on (wrapping around).
        # differs[i] says that the two values differ, posted as an exclusive or.
        differs = m.bool_vector(f"differs_{k}", n)
        for i in range(n):
            j = (i + k) % n
            # differs[i] <-> (plus[i] xor plus[j]), as four clauses
            m &= (~differs[i] | plus[i] | plus[j])
            m &= (~differs[i] | ~plus[i] | ~plus[j])
            m &= (differs[i] | ~plus[i] | plus[j])
            m &= (differs[i] | plus[i] | ~plus[j])
        d = m.int(f"d_{k}", 0, n)
        m &= (sum(differs[i] for i in range(n)) == d)

        # The cost of this lag is C_k^2 = (n - 2d)^2, a convex function of d, so it
        # is written as steps: going from t-1 to t differing positions changes
        # the cost by w_t. Where w_t is positive the step is paid when d >= t,
        # and a soft clause pays when its literal is false, so the literal is
        # the negation. Where w_t is negative the saving is written as the
        # same amount paid when d < t, which differs by a constant that does
        # not change which sequence is best.
        for t in range(1, n + 1):
            step = (n - 2 * t) ** 2 - (n - 2 * (t - 1)) ** 2
            if step > 0:
                m.obj[step] += ~(d >= t)
            elif step < 0:
                m.obj[-step] += (d >= t)

    return m, {"sequence": sequence}
