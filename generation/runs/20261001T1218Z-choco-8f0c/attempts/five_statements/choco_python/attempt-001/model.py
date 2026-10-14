# Five statements: statement i says "exactly i of these statements are false", for i = 1..5.
# Which statements are true?
from pychoco.model import Model

# The puzzle has no instance data; the five statements are its statement.
N = 5


def build(instance):
    del instance  # the puzzle carries no instance data

    model = Model()

    # statements[i] is true when statement i+1 is true
    statements = [model.boolvar(name=f"statement_{i}") for i in range(N)]
    # the number of false statements
    n_false = model.intvar(0, N, name="n_false")
    model.sum(statements + [n_false], "=", N).post()

    # Statement i+1 is true exactly when exactly i+1 statements are false.
    for i in range(N):
        model.arithm(n_false, "=", i + 1).reify_with(statements[i])

    return model, {"statements": statements}
