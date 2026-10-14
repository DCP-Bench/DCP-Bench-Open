#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Dudeney numbers: find a number larger than 1 with at most n digits that is
// a perfect cube whose cube root equals the sum of its digits.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int n = instance.at("n").get<int>();

  int64_t power = 1;  // 10^n
  for (int i = 0; i < n; ++i) power *= 10;

  // digits[i] is the i-th decimal digit, most significant first.
  std::vector<IntVar> digits;
  for (int i = 0; i < n; ++i) digits.push_back(model.NewIntVar(Domain(0, 9)));
  const IntVar number = model.NewIntVar(Domain(0, power - 1));
  // The cube root is a digit sum, so it lies between 1 and 9 * n.
  const IntVar cube_root = model.NewIntVar(Domain(1, 9 * n));

  // The number is the cube of its cube root (built two factors at a time).
  const IntVar square = model.NewIntVar(Domain(1, static_cast<int64_t>(9 * n) * (9 * n)));
  model.AddMultiplicationEquality(square, {cube_root, cube_root});
  model.AddMultiplicationEquality(number, {square, cube_root});

  // The cube root equals the sum of the digits.
  LinearExpr digit_sum;
  for (const IntVar& d : digits) digit_sum += d;
  model.AddEquality(cube_root, digit_sum);

  // The digits spell the number.
  LinearExpr spelled;
  int64_t weight = power / 10;
  for (int i = 0; i < n; ++i) {
    spelled += weight * digits[i];
    weight /= 10;
  }
  model.AddEquality(number, spelled);

  // The number is larger than 1.
  model.AddGreaterThan(number, 1);

  outputs = {{"number", number.index()}};
}
