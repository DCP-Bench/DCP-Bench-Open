# Finding celebrities: at a party, a celebrity is a person whom everybody
# knows and who knows only celebrities. Find who the celebrities are, given
# who knows whom; at least one celebrity is present.
from hermax.model import Model


def build(instance):
    graph = instance["graph"]  # graph[i][j] = 1 when person i knows person j
    n = len(graph)

    m = Model()
    # celebrities[i] = person i is a celebrity
    celebrities = m.bool_vector("celebrities", n)
    # num_celebrities = how many celebrities there are (at least one)
    num_celebrities = m.int("num_celebrities", 1, n)
    m &= (sum(celebrities[i] for i in range(n)) == num_celebrities)

    # A celebrity is known by everybody and knows only celebrities. As in the
    # problem's model, the second condition is stated as "the number of people
    # i knows equals the number of celebrities". Both counts come from the
    # instance, so each person is either impossible (not known by all) or a
    # celebrity exactly when num_celebrities equals the number of people they know.
    for i in range(n):
        known_by = sum(graph[j][i] for j in range(n))  # people who know i
        knows = sum(graph[i][j] for j in range(n))  # people i knows
        if known_by == n and 1 <= knows <= n:
            m &= (~celebrities[i] | (num_celebrities == knows))
            m &= (celebrities[i] | ~(num_celebrities == knows))
        else:
            m &= ~celebrities[i]

    return m, {"celebrities": celebrities}
