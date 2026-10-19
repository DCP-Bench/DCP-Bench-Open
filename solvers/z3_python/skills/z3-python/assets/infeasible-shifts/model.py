"""Three staff, each working 0 to 3 hours, must cover exactly 10 hours in total. This cannot be done."""
import z3

MAX_HOURS_EACH = 3
REQUIRED_TOTAL = 10

hours = z3.Ints("ann ben cara")
solver = z3.Solver()
solver.add([z3.And(h >= 0, h <= MAX_HOURS_EACH) for h in hours])
solver.add(z3.Sum(hours) == REQUIRED_TOTAL)

status = solver.check()
print(f"status: {status}")
if status == z3.unsat:
    print("No roster exists: the most hours that can be covered is "
          f"{MAX_HOURS_EACH * len(hours)}.")
elif status == z3.sat:
    print("roster:", {str(h): solver.model().eval(h, model_completion=True) for h in hours})
else:
    print(f"unknown: {solver.reason_unknown()}")
