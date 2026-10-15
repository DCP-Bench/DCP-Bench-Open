"""Every menu of three dishes whose calories stay within a limit."""
import cpmpy as cp

dishes = ["soup", "salad", "pasta", "fish", "cake"]
calories = [180, 250, 520, 390, 410]
LIMIT = 1000

pick = cp.boolvar(shape=len(dishes), name="pick")  # one Boolean per dish: on the menu or not
model = cp.Model(
    cp.sum(pick) == 3,
    cp.sum([c * p for c, p in zip(calories, pick)]) <= LIMIT,
)

menus = []


def record():
    # Called once per solution; the outputs are the Booleans, so each menu appears once.
    menus.append(tuple(dishes[i] for i in range(len(dishes)) if pick[i].value()))


count = model.solveAll(display=record)
print("Solutions:", count)
for menu in sorted(menus):
    print("  " + ", ".join(menu))
