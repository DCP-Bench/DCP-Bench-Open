// Enumerate every subset of {2, 3, 4, 5, 6, 7} whose sum is 10.
#include <iostream>
#include <vector>

#include "ortools/sat/cp_model.h"
#include "ortools/sat/cp_model_solver.h"
#include "ortools/sat/model.h"
#include "ortools/sat/sat_parameters.pb.h"

using namespace operations_research;
using namespace operations_research::sat;

int main() {
  const std::vector<int> values = {2, 3, 4, 5, 6, 7};
  const int target = 10;

  CpModelBuilder model;
  std::vector<BoolVar> take;
  LinearExpr total;
  for (int value : values) {
    BoolVar chosen = model.NewBoolVar();
    take.push_back(chosen);
    total += value * chosen;
  }
  model.AddEquality(total, target);

  // Every variable of the model is a decision variable here, so each solution
  // is one distinct subset. With auxiliary variables, enumeration would report
  // one solution per auxiliary assignment (see the README of this example).
  Model enumerator;
  int count = 0;
  enumerator.Add(NewFeasibleSolutionObserver([&](const CpSolverResponse& r) {
    ++count;
    std::cout << "Solution " << count << ":";
    for (size_t i = 0; i < values.size(); ++i) {
      if (SolutionBooleanValue(r, take[i])) std::cout << " " << values[i];
    }
    std::cout << "\n";
  }));

  SatParameters parameters;
  parameters.set_enumerate_all_solutions(true);
  parameters.set_num_workers(1);
  enumerator.Add(NewSatParameters(parameters));

  const CpSolverResponse response = SolveCpModel(model.Build(), &enumerator);
  std::cout << "Status: " << CpSolverStatus_Name(response.status()) << "\n";
  std::cout << "Total solutions: " << count << "\n";
  return 0;
}
