# Low autocorrelation binary sequence: find a sequence of n bits, each +1 or -1,
# that minimises the sum of the squared periodic autocorrelations.
from pychoco.model import Model


def build(instance):
    n = instance["n"]  # length of the binary sequence

    model = Model()

    # sequence[i] is +1 or -1 (the value 0 is excluded by giving the variable only these two values)
    sequence = [model.intvar([-1, 1], name=f"sequence_{i}") for i in range(n)]

    # energy = sum over shifts s = 1..n-1 of (periodic autocorrelation at shift s) squared
    squared_correlations = []
    for s in range(1, n):
        # the products sequence[i] * sequence[(i + s) mod n] around the cycle
        products = []
        for i in range(n):
            product = model.intvar([-1, 1], name=f"product_{s}_{i}")
            model.times(sequence[i], sequence[(i + s) % n], product).post()
            products.append(product)
        # periodic autocorrelation at shift s = sum of those products
        correlation = model.intvar(-n, n, name=f"correlation_{s}")
        model.sum(products, "=", correlation).post()
        # its square
        squared = model.intvar(0, n * n, name=f"squared_{s}")
        model.square(squared, correlation).post()
        squared_correlations.append(squared)

    energy = model.intvar(0, (n - 1) * n * n, name="energy")
    model.sum(squared_correlations, "=", energy).post()

    # minimise the energy (Choco optimises a single variable)
    return model, {"sequence": sequence}, ("minimize", energy)
