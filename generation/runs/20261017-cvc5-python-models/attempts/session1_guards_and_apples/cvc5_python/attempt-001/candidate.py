# Problem: session1_guards_and_apples
# A boy wants to give an apple to a girl. To get to her, he has to pass through a number of gates,
# each with a guard. He bribes each guard with half of his apples, plus one. The boy does not have
# a knife, therefore he gives the guard an integer number of apples. After he's given the apple to
# the girl, he has no apples left. Print a list of numbers (apples), containing the number of apples
# before each gate, plus the number of apples after the last gate, so in total num_gates + 1 numbers.

from cvc5.pythonic import Ints


def build(instance):
    num_gates = instance["num_gates"]
    apples = Ints(" ".join(f"a{i}" for i in range(num_gates + 1)))

    constraints = []

    # After he has given the apple to the girl, he has no apples left: he holds exactly one apple
    # at the end, the one he gives her.
    constraints.append(apples[num_gates] == 1)

    # Each guard is bribed with half of his apples plus one. The bribe is an integer number of
    # apples, so the number of apples before each gate is even, and the apples left after the gate
    # are the apples before it minus (half of them plus one).
    # Writing the apples before gate i as 2*h, the bribe is h + 1 and the apples left are h - 1.
    # Each gate gives: apples[i] - (apples[i] / 2 + 1) == apples[i + 1], with apples[i] even.
    for i in range(num_gates):
        constraints.append(apples[i] == 2 * (apples[i + 1] + 1))

    # Apples are never negative.
    for a in apples:
        constraints.append(a >= 0)

    return constraints, {"apples": apples}
