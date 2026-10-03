#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// De Bruijn sequence: find a cyclic sequence of length base^n over an alphabet
// of `base` symbols in which every possible length-n string occurs exactly
// once as a (cyclic) substring.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int base = instance.at("base").get<int>();
  const int n = instance.at("n").get<int>();

  // Sequence length: one position per possible length-n string, base^n of them.
  int64_t m = 1;
  for (int j = 0; j < n; ++j) m *= base;

  // de_bruijn[i] is the symbol at position i of the cyclic sequence.
  std::vector<IntVar> de_bruijn;
  for (int64_t i = 0; i < m; ++i) de_bruijn.push_back(model.NewIntVar(Domain(0, base - 1)));

  // x[i] is the number whose n base-digits are the symbols read from position i
  // onwards (wrapping around the end, since the sequence is cyclic).
  // Reading the window straight off the sequence expresses the reference's
  // "each window is the previous one shifted by one symbol, also around the
  // corner" with no separate digit matrix.
  std::vector<IntVar> x;
  for (int64_t i = 0; i < m; ++i) {
    LinearExpr window;
    int64_t weight = m / base;  // base^(n-1): the first symbol is the most significant digit
    for (int j = 0; j < n; ++j) {
      window += weight * de_bruijn[(i + j) % m];
      weight /= base;
    }
    const IntVar number = model.NewIntVar(Domain(0, m - 1));
    model.AddEquality(number, window);
    x.push_back(number);
  }

  // Every length-n string occurs exactly once: the m window numbers are all different.
  model.AddAllDifferent(x);

  json out = json::array();
  for (const IntVar& v : de_bruijn) out.push_back(v.index());
  outputs = {{"de_bruijn", out}};
}
