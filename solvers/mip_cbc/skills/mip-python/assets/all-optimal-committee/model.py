# All optimal committees: choose 3 of 6 candidates to maximise the total score, and list every
# committee that reaches the best score.
# Method: solve, check the optimum is proven, pin the objective to that value, then enumerate
# with a no-good cut over the choice binaries (they are the only outputs).
import mip

scores = [5, 5, 3, 3, 3, 1]
size = 3

m = mip.Model(sense=mip.MAXIMIZE, solver_name="CBC")
m.verbose = 0
m.max_mip_gap = 0.0
m.max_mip_gap_abs = 0.0
pick = [m.add_var(f"pick_{i}", var_type=mip.BINARY) for i in range(len(scores))]

# exactly `size` candidates are chosen
m += mip.xsum(pick) == size

# the objective is the total score of the chosen candidates
m.objective = mip.xsum(scores[i] * pick[i] for i in range(len(scores)))

status = m.optimize(max_seconds=60)
if status != mip.OptimizationStatus.OPTIMAL:
    raise SystemExit(f"Status: {status.name}")
best = round(m.objective_value)
print("Optimal score:", best)

# pin the objective to the proven optimum, so only optimal committees remain
m += m.objective >= best - 1e-6
m += m.objective <= best + 1e-6

committees = []
while m.optimize(max_seconds=60) == mip.OptimizationStatus.OPTIMAL:
    chosen = tuple(i for i in range(len(scores)) if pick[i].x > 0.5)
    committees.append(chosen)
    # no-good: at least one of the chosen candidates is dropped, or one other is added
    m += mip.xsum((1 - pick[i]) if i in chosen else pick[i] for i in range(len(scores))) >= 1

print("Optimal committees:", len(committees))
for committee in committees:
    print("  candidates", [i + 1 for i in committee])
