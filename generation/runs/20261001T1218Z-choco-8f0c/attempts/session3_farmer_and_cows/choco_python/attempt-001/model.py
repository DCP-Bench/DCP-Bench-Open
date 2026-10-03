# Farmer and cows: cow number k gives k units of milk. Distribute all cows among the sons,
# each son getting a given number of cows, so that every son gets the same total quantity
# of milk.
from pychoco.model import Model


def build(instance):
    num_cows = instance["num_cows"]
    num_sons = instance["num_sons"]
    cows_per_son = instance["cows_per_son"]  # cows_per_son[s] = number of cows son s gets

    # cow c (counting from 0) gives c + 1 units of milk
    milk_per_cow = list(range(1, num_cows + 1))
    total_milk = sum(milk_per_cow)
    total_milk_per_son = total_milk // num_sons  # what each son must get

    model = Model()

    # cow_assignments[c] = the son (0..num_sons-1) who gets cow c
    cow_assignments = [model.intvar(0, num_sons - 1, name=f"cow_{c}") for c in range(num_cows)]

    # gets[s][c] is true when cow c goes to son s
    gets = [[model.arithm(cow_assignments[c], "=", s).reify() for c in range(num_cows)]
            for s in range(num_sons)]

    for s in range(num_sons):
        # each son gets a specific number of cows
        model.sum(gets[s], "=", cows_per_son[s]).post()
        # the milk of the cows of each son adds up to the same total
        model.scalar(gets[s], milk_per_cow, "=", total_milk_per_son).post()

    return model, {"cow_assignments": cow_assignments}
