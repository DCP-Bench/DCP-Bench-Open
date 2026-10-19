// Ages of the three sons of an old man (problem ages_of_the_sons).
// The product of the three ages is 36. The sum of their ages equals the number of
// windows in a building, which the mathematician cannot determine from the product
// alone: the sum must be shared by another triple with the same product. The oldest
// son is unique (he has blue eyes), which settles it. Outputs A1 >= A2 >= A3 are the
// ages starting from the oldest.
#include <array>
#include <vector>

#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  (void)instance;  // the statement fixes the product; the instance has no fields
  const int product = 36;  // the old man's product of ages, from the statement

  // every way to write the product as three positive ages a >= b >= c
  std::vector<std::array<int, 3>> triples;
  for (int a = 1; a <= product; ++a)
    for (int b = 1; b <= a; ++b)
      for (int c = 1; c <= b; ++c)
        if (a * b * c == product) triples.push_back({a, b, c});
  const int count = static_cast<int>(triples.size());

  // the sons' ages are exactly one of these triples: w[k] = 1 picks triple k
  std::vector<dcp::Lin> w;
  for (int k = 0; k < count; ++k) w.push_back(dcp::new_var(h, 0, 1));
  dcp::Lin picked;
  for (const auto& x : w) picked = picked + x;
  // exactly one triple is the sons' ages
  dcp::add_row(h, picked, 1, 1);

  // the sons' ages A1, A2, A3 (oldest first), each between 1 and the product
  dcp::Lin a1 = dcp::new_var(h, 1, product);
  dcp::Lin a2 = dcp::new_var(h, 1, product);
  dcp::Lin a3 = dcp::new_var(h, 1, product);
  dcp::Lin t1, t2, t3;
  for (int k = 0; k < count; ++k) {
    t1 = t1 + static_cast<double>(triples[k][0]) * w[k];
    t2 = t2 + static_cast<double>(triples[k][1]) * w[k];
    t3 = t3 + static_cast<double>(triples[k][2]) * w[k];
  }
  // the ages A1, A2, A3 are the picked triple
  dcp::add_row(h, a1 - t1, 0, 0);
  dcp::add_row(h, a2 - t2, 0, 0);
  dcp::add_row(h, a3 - t3, 0, 0);

  // the sum of the ages is ambiguous: another triple v[k] with the same product
  // has the same sum, and it is not the sons' own triple (v[k] + w[k] <= 1)
  std::vector<dcp::Lin> v;
  for (int k = 0; k < count; ++k) v.push_back(dcp::new_var(h, 0, 1));
  dcp::Lin other;
  for (const auto& x : v) other = other + x;
  // one other triple is chosen; its sum is checked against the sons' sum below
  dcp::add_row(h, other, 1, 1);
  for (int k = 0; k < count; ++k) {
    // the other triple is not the sons' own triple
    dcp::add_row(h, v[k] + w[k], -kHighsInf, 1);
  }
  dcp::Lin other_sum;
  for (int k = 0; k < count; ++k) {
    int s = triples[k][0] + triples[k][1] + triples[k][2];
    other_sum = other_sum + static_cast<double>(s) * v[k];
  }
  // the other triple has the same sum of ages as the sons
  dcp::add_row(h, other_sum - (a1 + a2 + a3), 0, 0);

  // the oldest son is unique: A1 is strictly older than A2
  dcp::add_row(h, a1 - a2, 1, kHighsInf);

  out.add("A1", a1);
  out.add("A2", a2);
  out.add("A3", a3);
}
