#include <cstdint>
#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Divisible by 1 through 9 (and 10): find a ten-digit number that uses each
// digit 0-9 exactly once, such that the number formed by its first n digits,
// read from the left, is divisible by n for every n from 1 to 10.
// The problem has no instance data. CP-SAT integers are 64-bit, so the
// ten-digit number fits in one variable.
void Build(const json& /*instance*/, CpModelBuilder& model, json& outputs) {
  const int kDigits = 10;
  const int64_t kMax = 10000000000LL;  // 10^10, the bound the statement's prefixes stay under

  std::vector<IntVar> x;  // the ten digits, left to right
  std::vector<IntVar> t;  // t[i]: the number formed by the first i+1 digits
  for (int i = 0; i < kDigits; ++i) {
    x.push_back(model.NewIntVar(Domain(0, 9)));
    t.push_back(model.NewIntVar(Domain(0, kMax)));
  }

  // Each digit 0-9 is used exactly once.
  model.AddAllDifferent(x);

  for (int i = 0; i < kDigits; ++i) {
    // The number formed by the first i+1 digits.
    LinearExpr prefix;
    int64_t power = 1;
    for (int j = i; j >= 0; --j) {
      prefix += power * x[j];
      power *= 10;
    }
    model.AddEquality(t[i], prefix);

    // That number is divisible by i+1: it equals (i+1) times some integer
    // quotient, a linear form of t[i] % (i+1) == 0.
    const IntVar quotient = model.NewIntVar(Domain(0, kMax / (i + 1)));
    model.AddEquality(t[i], (i + 1) * quotient);
  }

  outputs = {{"number", t[kDigits - 1].index()}};
}
