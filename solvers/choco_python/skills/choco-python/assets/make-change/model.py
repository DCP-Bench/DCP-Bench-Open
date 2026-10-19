from pychoco.model import Model

AMOUNT = 10
COINS = [1, 2, 5]
MAX_COUNT = AMOUNT  # enough for every coin

model = Model()
counts = [model.intvar(0, MAX_COUNT, name=f"coin{c}") for c in COINS]
# The amount is a function of the counts, so fixing the counts fixes it:
# no duplicate solutions come from it.
total = model.intvar(AMOUNT, AMOUNT, name="total")
model.scalar(counts, COINS, "=", total).post()

solutions = model.get_solver().find_all_solutions()
print(f"Ways to pay {AMOUNT} with coins {COINS}: {len(solutions)}")
for solution in solutions:
    picks = [solution.get_int_val(c) for c in counts]
    print("  " + ", ".join(f"{n} x {c}" for n, c in zip(picks, COINS)))
