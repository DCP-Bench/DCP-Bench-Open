from pycsp3 import *

# Handshaking: num_couples invited couples, plus Hilary and Jocelyn, shake hands with each other.
# Nobody shakes hands with himself, herself or the spouse. All the numbers of hands are different.
# Print the number of hands Hilary has shaken.
# num_couples counts the invited couples; Hilary and Jocelyn are one more couple
n_couples = data.num_couples + 1
n_people = 2 * n_couples

# person 0 is Hilary, person 1 is Jocelyn; persons 2k and 2k+1 are the other couples, so the spouse of p
# is p + 1 when p is even and p - 1 when p is odd
def spouse(p):
    return p + 1 if p % 2 == 0 else p - 1

# shakes[p][q] is 1 iff person p shakes hands with person q
shakes = VarArray(size=[n_people, n_people], dom={0, 1})
# hands[p] is the number of hands person p has shaken
hands = VarArray(size=n_people, dom=range(n_people - 1))
# hil is the number of hands Hilary has shaken
hil = Var(dom=range(n_people - 1))

satisfy(
    # nobody shakes hands with himself or herself
    [shakes[p][p] == 0 for p in range(n_people)],
    # nobody shakes hands with his or her spouse
    [shakes[p][spouse(p)] == 0 for p in range(n_people)],
    # a handshake is between two people, so it is the same from both sides
    [shakes[p][q] == shakes[q][p] for p in range(n_people) for q in range(n_people) if p < q],
    # the number of hands of each person is the number of handshakes he or she takes part in
    [hands[p] == Sum(shakes[p]) for p in range(n_people)],
    # all the answers are different; Jocelyn is the one who asks, so her own answer is not among them
    AllDifferent([hands[p] for p in range(n_people) if p != 1]),
    # Hilary is person 0, and hil is the number of hands Hilary has shaken
    hil == hands[0],
)
