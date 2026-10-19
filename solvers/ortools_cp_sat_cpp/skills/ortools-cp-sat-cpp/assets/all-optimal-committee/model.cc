// Choose 3 of 6 candidates at minimum total cost, with at least one candidate
// from group A (0..2) and one from group B (3..5). Then list every optimal choice.
#include <cstdint>
#include <iostream>
#include <vector>

#include "ortools/sat/cp_model.h"
#include "ortools/sat/cp_model_solver.h"
#include "ortools/sat/model.h"
#include "ortools/sat/sat_parameters.pb.h"

using namespace operations_research;
using namespace operations_research::sat;

const std::vector<int> kCost = {4, 2, 3, 3, 3, 6};

// Adds the variables and constraints; fills in the choice flags and the cost.
void BuildCommittee(CpModelBuilder& model, std::vector<BoolVar>& pick,
                    LinearExpr& cost) {
  LinearExpr size;
  for (size_t i = 0; i < kCost.size(); ++i) {
    pick.push_back(model.NewBoolVar());
    cost += kCost[i] * pick.back();
    size += pick.back();
  }
  model.AddEquality(size, 3);
  model.AddBoolOr({pick[0], pick[1], pick[2]});
  model.AddBoolOr({pick[3], pick[4], pick[5]});
}

int main() {
  // Phase 1: find the optimum.
  CpModelBuilder first;
  std::vector<BoolVar> pick_first;
  LinearExpr cost_first;
  BuildCommittee(first, pick_first, cost_first);
  first.Minimize(cost_first);
  const CpSolverResponse best = Solve(first.Build());
  if (best.status() != CpSolverStatus::OPTIMAL) {
    std::cout << "Status: " << CpSolverStatus_Name(best.status()) << "\n";
    return 0;
  }
  const int64_t optimum = static_cast<int64_t>(best.objective_value());
  std::cout << "Optimal cost: " << optimum << "\n";

  // Phase 2: a fresh model with cost fixed to the optimum and no objective;
  // enumerate its solutions. The choice flags are the only decision variables.
  CpModelBuilder second;
  std::vector<BoolVar> pick;
  LinearExpr cost;
  BuildCommittee(second, pick, cost);
  second.AddEquality(cost, optimum);

  Model enumerator;
  int count = 0;
  enumerator.Add(NewFeasibleSolutionObserver([&](const CpSolverResponse& r) {
    ++count;
    std::cout << "Optimal choice " << count << ":";
    for (size_t i = 0; i < pick.size(); ++i) {
      if (SolutionBooleanValue(r, pick[i])) std::cout << " " << i;
    }
    std::cout << "\n";
  }));
  SatParameters parameters;
  parameters.set_enumerate_all_solutions(true);
  parameters.set_num_workers(1);
  enumerator.Add(NewSatParameters(parameters));
  SolveCpModel(second.Build(), &enumerator);
  std::cout << "Optimal choices: " << count << "\n";
  return 0;
}
