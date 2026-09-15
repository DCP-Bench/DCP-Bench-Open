#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// ISBN-13: recover the digits marked -1, respecting the 978/979 prefix and the
// weighted check-digit rule.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const std::vector<int64_t> isbn_init =
      instance.at("isbn_init").get<std::vector<int64_t>>();
  const int n = static_cast<int>(isbn_init.size());

  std::vector<IntVar> isbn;
  for (int i = 0; i < n; ++i) isbn.push_back(model.NewIntVar(Domain(0, 9)));

  // Anything not marked -1 is already known.
  for (int i = 0; i < n; ++i) {
    if (isbn_init[i] != -1) model.AddEquality(isbn[i], isbn_init[i]);
  }

  // ISBN-13 prefixes: 978 or 979.  These belong to the numbering scheme rather
  // than the instance, and the reference fixes them the same way.
  model.AddEquality(isbn[0], 9);
  model.AddEquality(isbn[1], 7);
  model.AddLinearConstraint(isbn[2], Domain::FromValues({8, 9}));

  // Check digit: 10 - (weighted sum mod 10), itself taken mod 10 so that a
  // remainder of zero gives a check digit of zero rather than ten.
  LinearExpr weighted;
  for (int i = 0; i < n - 1; ++i) weighted += (i % 2 == 0 ? 1 : 3) * isbn[i];
  IntVar check_sum = model.NewIntVar(Domain(0, int64_t{9} * 3 * (n - 1)));
  model.AddEquality(check_sum, weighted);

  IntVar remainder = model.NewIntVar(Domain(0, 9));
  model.AddModuloEquality(remainder, check_sum, 10);

  IntVar complement = model.NewIntVar(Domain(1, 10));
  model.AddEquality(complement, 10 - remainder);

  IntVar check_digit = model.NewIntVar(Domain(0, 9));
  model.AddModuloEquality(check_digit, complement, 10);
  model.AddEquality(isbn[n - 1], check_digit);

  json out = json::array();
  for (const IntVar& d : isbn) out.push_back(d.index());
  outputs = {{"isbn", out}};
}
