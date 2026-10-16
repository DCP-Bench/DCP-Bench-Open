from pycsp3 import *

# the five children, the ages, the countries and the stories are linked by a shared slot number from 1 to 5
AGES = [3, 5, 7, 8, 10]
# ages[a] is the slot of the age AGES[a]; children[c] is the slot of child c (Bernice, Carl, Debby, Sammy, Ted)
ages = VarArray(size=5, dom=range(1, 6))
children = VarArray(size=5, dom=range(1, 6))
# countries[k] is the slot of country k (Ethiopia, Kazakhstan, Lithuania, Morocco, Yemen)
countries = VarArray(size=5, dom=range(1, 6))
# stories[s] is the slot of story s (burning bush, captivity, Moses's youth, Passover, Ten Commandments)
stories = VarArray(size=5, dom=range(1, 6))
# slot_age[k] is the age of the family and child in slot k + 1
slot_age = VarArray(size=5, dom={3, 5, 7, 8, 10})
satisfy(
    # each slot number is used once in each of the four lists
    AllDifferent(ages),
    AllDifferent(children),
    AllDifferent(countries),
    AllDifferent(stories),
    # the age of the slot is the age given by its position in the ages list
    [imply(ages[a] == k + 1, slot_age[k] == AGES[a]) for a in range(5) for k in range(5)],
    # Debby's family is from Lithuania
    children[2] == countries[2],
    # the child who told the story of the Passover is two years older than Bernice
    slot_age[stories[3] - 1] == slot_age[children[0] - 1] + 2,
    # the child whose family is from Yemen is younger than the child from the Ethiopian family
    slot_age[countries[4] - 1] < slot_age[countries[0] - 1],
    # the child from the Moroccan family is three years older than Ted
    slot_age[countries[3] - 1] == slot_age[children[4] - 1] + 3,
    # Sammy is three years older than the child who told the story of Moses's youth
    slot_age[children[3] - 1] == slot_age[stories[2] - 1] + 3,
)
