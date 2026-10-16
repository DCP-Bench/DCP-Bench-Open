// Problem: age_changing. Let m be my age and h my husband's age. Starting from my age and applying
// the four operations +2, /8, -3, *7, each once and in some order, gives his age. Starting from his
// age and applying the same four operations in a different order gives my age. Report (h, m).
// The instance has no fields: the operations and the age range are fixed by the problem statement.
#include "dcp.h"

#include <algorithm>
#include <array>
#include <vector>

namespace {

enum Op { PLUS2, DIV8, MINUS3, TIMES7 };

// Largest age in years. An assumption about the problem's domain, not a value taken from the instance.
const int kMaxAge = 150;
// Largest value on any chain: start at kMaxAge, +2, then *7 is the largest step (7 * (kMaxAge + 2)).
const double kMaxValue = 7.0 * (kMaxAge + 2);
// Big-M: |expr - rhs| is at most 8 * kMaxValue on every chain row (x - 8y, y - 7x, v - age).
const double kBigM = 8.0 * kMaxValue + 10;

// Enforces expr = rhs when s = 1, and nothing when s = 0.
// expr - rhs <= M (1 - s) and expr - rhs >= -M (1 - s).
void enforce_if(Highs& h, const dcp::Lin& expr, double rhs, const dcp::Lin& s) {
  dcp::add_row(h, expr + kBigM * s, -kHighsInf, rhs + kBigM);
  dcp::add_row(h, expr - kBigM * s, rhs - kBigM, kHighsInf);
}

// One chain: the value starts at `start`, applies the four operations in the order `ops`,
// and ends at `end`. The chain is active only when the order indicator `s` is 1.
void chain(Highs& h, const std::array<int, 4>& ops, const dcp::Lin& start, const dcp::Lin& end,
           const dcp::Lin& s) {
  std::vector<dcp::Lin> v;
  for (int k = 0; k < 5; k++) v.push_back(dcp::new_var(h, 0, kMaxValue));

  // the chain begins with the starting age
  enforce_if(h, v[0] - start, 0, s);
  // the chain ends with the target age
  enforce_if(h, v[4] - end, 0, s);

  for (int k = 0; k < 4; k++) {
    const dcp::Lin& x = v[k];
    const dcp::Lin& y = v[k + 1];
    switch (ops[k]) {
      case PLUS2:
        // the result is the value plus 2
        enforce_if(h, y - x, 2, s);
        break;
      case MINUS3:
        // the result is the value minus 3
        enforce_if(h, y - x, -3, s);
        break;
      case TIMES7:
        // the result is seven times the value
        enforce_if(h, y - 7.0 * x, 0, s);
        break;
      case DIV8:
        // the value is divisible by 8 and the result is the value divided by 8
        enforce_if(h, x - 8.0 * y, 0, s);
        break;
    }
  }
}

}  // namespace

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  (void)instance;

  dcp::Lin mine = dcp::new_var(h, 0, kMaxAge);
  dcp::Lin husband = dcp::new_var(h, 0, kMaxAge);

  // every order of the four operations
  std::array<int, 4> perm = {PLUS2, DIV8, MINUS3, TIMES7};
  std::vector<std::array<int, 4>> orders;
  do {
    orders.push_back(perm);
  } while (std::next_permutation(perm.begin(), perm.end()));
  const size_t K = orders.size();

  // s1[k] = 1 when the first chain (my age to his) uses order k; s2[k] likewise for the second chain
  std::vector<dcp::Lin> s1, s2;
  for (size_t k = 0; k < K; k++) s1.push_back(dcp::new_var(h, 0, 1));
  for (size_t k = 0; k < K; k++) s2.push_back(dcp::new_var(h, 0, 1));

  // exactly one order is used by each chain
  dcp::Lin sum1, sum2;
  for (size_t k = 0; k < K; k++) {
    sum1 = sum1 + s1[k];
    sum2 = sum2 + s2[k];
  }
  dcp::add_row(h, sum1, 1, 1);
  dcp::add_row(h, sum2, 1, 1);

  // the two chains use different orders
  for (size_t k = 0; k < K; k++) dcp::add_row(h, s1[k] + s2[k], -kHighsInf, 1);

  for (size_t k = 0; k < K; k++) chain(h, orders[k], mine, husband, s1[k]);
  for (size_t k = 0; k < K; k++) chain(h, orders[k], husband, mine, s2[k]);

  out.add("h", husband);
  out.add("m", mine);
}
