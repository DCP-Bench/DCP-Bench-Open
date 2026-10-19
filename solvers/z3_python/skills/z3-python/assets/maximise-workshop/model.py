"""Maximise profit from making chairs and tables under labour and wood limits, with Z3."""
import z3

PROFIT = {"chairs": 4, "tables": 9}
WOOD = {"chairs": 2, "tables": 4}      # wood units per item
HOURS = {"chairs": 3, "tables": 2}     # labour hours per item
WOOD_STOCK, HOURS_AVAILABLE = 40, 30

chairs, tables = z3.Ints("chairs tables")
optimizer = z3.Optimize()
optimizer.add(chairs >= 0, tables >= 0)
optimizer.add(WOOD["chairs"] * chairs + WOOD["tables"] * tables <= WOOD_STOCK)
optimizer.add(HOURS["chairs"] * chairs + HOURS["tables"] * tables <= HOURS_AVAILABLE)
profit = PROFIT["chairs"] * chairs + PROFIT["tables"] * tables
handle = optimizer.maximize(profit)

if optimizer.check() != z3.sat:
    raise SystemExit(f"status: {optimizer.check()}")
model = optimizer.model()
print(f"chairs: {model[chairs]}, tables: {model[tables]}")
print(f"Maximum profit: {optimizer.upper(handle)}")
print(f"proven optimal: {optimizer.lower(handle).as_long() == optimizer.upper(handle).as_long()}")
