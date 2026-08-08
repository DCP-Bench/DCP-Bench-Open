#!/usr/bin/env python3
"""Warehouse-location and distribution problem solved with Google OR-Tools CP-SAT.

Outputs a JSON object with keys in the exact order:
['total_cost', 'ships', 'open_warehouse']
"""
import json
from collections import OrderedDict
from ortools.sat.python import cp_model


def main() -> None:
    # ------------------------------------------------------------------
    # 1. Immutable input data (exactly as provided in the statement)
    # ------------------------------------------------------------------
    warehouse_s = ["New York", "Los Angeles", "Chicago", "Atlanta"]
    fixed_costs = [400, 500, 300, 150]      # weekly fixed costs per warehouse
    max_shipping = 100                      # capacity (units/week) per warehouse

    demands = [80, 70, 40]                  # weekly demand for regions 1–3

    shipping_costs = [                      # cost per unit shipped
        [20, 40, 50],   # New York → regions 1,2,3
        [48, 15, 26],   # Los Angeles
        [26, 35, 18],   # Chicago
        [24, 50, 35],   # Atlanta
    ]

    num_warehouses = len(warehouse_s)
    num_regions = len(demands)

    # ------------------------------------------------------------------
    # 2. Build CP-SAT model
    # ------------------------------------------------------------------
    model = cp_model.CpModel()

    # 2.1 Decision variables
    open_warehouse = [model.NewBoolVar(f"open[{j}]")
                      for j in range(num_warehouses)]

    # Ship units from warehouse j to region r.
    # Upper bound: cannot exceed overall warehouse capacity (100) but use a
    # slightly larger bound to stay safe and future-proof.
    ship_ub = max(max_shipping, max(demands))  # 100 here
    ships = [[model.NewIntVar(0, ship_ub, f"ship[{j},{r}]")
              for r in range(num_regions)]
             for j in range(num_warehouses)]

    # Upper bound for total cost: fixed + (worst per-unit cost * max units).
    max_total_fixed = sum(fixed_costs)                 # = 1350
    max_per_unit_cost = max(c for row in shipping_costs for c in row)  # = 50
    max_units_possible = max_shipping * 3              # at most 3 warehouses open
    total_cost_ub = max_total_fixed + max_per_unit_cost * max_units_possible  # 1350 + 50*300 = 16350
    total_cost = model.NewIntVar(0, total_cost_ub, "total_cost")

    # ------------------------------------------------------------------
    # 3. Constraints
    # ------------------------------------------------------------------
    # 3.1 Demand satisfaction (≥ demand)
    for r in range(num_regions):
        model.Add(sum(ships[j][r] for j in range(num_warehouses)) >= demands[r])

    # 3.2 Warehouse capacity & linking: shipments out ≤ capacity × open
    for j in range(num_warehouses):
        model.Add(sum(ships[j][r] for r in range(num_regions)) <=
                  max_shipping * open_warehouse[j])

    # 3.3 Logical implication: New York ⇒ Los Angeles (indices 0 ⇒ 1)
    model.AddImplication(open_warehouse[0], open_warehouse[1])

    # 3.4 No more than 3 warehouses can be opened
    model.Add(sum(open_warehouse) <= 3)

    # 3.5 Either Atlanta (3) or Los Angeles (1) must be open
    model.Add(open_warehouse[3] + open_warehouse[1] >= 1)

    # 3.6 Cost definition
    fixed_cost_term = sum(fixed_costs[j] * open_warehouse[j]
                          for j in range(num_warehouses))
    shipping_cost_term = sum(shipping_costs[j][r] * ships[j][r]
                             for j in range(num_warehouses)
                             for r in range(num_regions))
    model.Add(total_cost == fixed_cost_term + shipping_cost_term)

    # ------------------------------------------------------------------
    # 4. Objective – minimise total weekly cost
    # ------------------------------------------------------------------
    model.Minimize(total_cost)

    # ------------------------------------------------------------------
    # 5. Solve
    # ------------------------------------------------------------------
    solver = cp_model.CpSolver()
    # Optional: small time limit to prevent runaway in pathological cases
    solver.parameters.max_time_in_seconds = 30

    status = solver.Solve(model)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        raise RuntimeError("No feasible solution found.")

    # ------------------------------------------------------------------
    # 6. Extract results
    # ------------------------------------------------------------------
    open_solution = [int(solver.Value(open_warehouse[j]))
                     for j in range(num_warehouses)]
    ships_solution = [[int(solver.Value(ships[j][r]))
                       for r in range(num_regions)]
                      for j in range(num_warehouses)]

    # Build result in the required key order
    result = OrderedDict()
    result["total_cost"] = int(solver.Value(total_cost))
    result["ships"] = ships_solution
    result["open_warehouse"] = open_solution

    # ------------------------------------------------------------------
    # 7. Output JSON (nothing else)
    # ------------------------------------------------------------------
    print(json.dumps(result))


if __name__ == "__main__":
    main()
