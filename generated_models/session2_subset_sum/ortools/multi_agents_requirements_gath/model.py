# Complete, runnable Python program that determines how many bags of each size were stolen
# so that exactly 100 coins are missing.

import json
from ortools.sat.python import cp_model


def main():
    # ------------------------------------------------------------------
    # Immutable problem data (directly taken from the requirement block)
    # ------------------------------------------------------------------
    coins_per_bag = [16, 17, 23, 24, 39, 40]  # coins contained in each bag type
    total_loss = 100                          # total number of coins stolen

    # ------------------------------------------------------------------
    # CP-SAT model definition
    # ------------------------------------------------------------------
    model = cp_model.CpModel()

    # Decision variables: bags[i] = number of stolen bags of type i
    # An upper bound of total_loss // min(coins_per_bag) is safe and small.
    max_bags = total_loss // min(coins_per_bag)  # 100 // 16 = 6
    bags = [model.NewIntVar(0, max_bags, f"bags_{c}") for c in coins_per_bag]

    # Coin-balance constraint: the stolen coins must add up to `total_loss`.
    model.Add(sum(c * bags[i] for i, c in enumerate(coins_per_bag)) == total_loss)

    # ------------------------------------------------------------------
    # Solve the model (pure feasibility problem, no objective needed)
    # ------------------------------------------------------------------
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # ------------------------------------------------------------------
    # Output
    # ------------------------------------------------------------------
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        result = {
            "bags": [solver.Value(b) for b in bags]  # ordered as required
        }
    else:
        # No feasible assignment exists (should not happen for this problem)
        result = {"bags": None}

    # Print ONLY the JSON result, exactly as requested
    print(json.dumps(result))


if __name__ == "__main__":
    main()
