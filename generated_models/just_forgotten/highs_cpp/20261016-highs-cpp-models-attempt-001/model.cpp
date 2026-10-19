// Joe's account number x is a list of the digits 0..n-1 in some order (n is the length of
// each set). Each set is also an ordering of the same digits, and in each set exactly
// num_correct_digits positions hold the same digit as x in that position.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const auto& sets = instance.at("sets");
  const int k = instance.at("num_correct_digits").get<int>();
  const int n = sets.empty() ? 0 : static_cast<int>(sets[0].size());

  // y[i][v] = 1 when the account number has digit v at position i.
  std::vector<std::vector<dcp::Lin>> y(n, std::vector<dcp::Lin>(n));
  for (int i = 0; i < n; ++i)
    for (int v = 0; v < n; ++v) y[i][v] = dcp::new_var(h, 0, 1);

  // each position of the account number holds exactly one digit
  for (int i = 0; i < n; ++i) {
    dcp::Lin one;
    for (int v = 0; v < n; ++v) one = one + y[i][v];
    dcp::add_row(h, one, 1, 1);
  }

  // each digit appears in exactly one position of the account number
  for (int v = 0; v < n; ++v) {
    dcp::Lin once;
    for (int i = 0; i < n; ++i) once = once + y[i][v];
    dcp::add_row(h, once, 1, 1);
  }

  // in each set, exactly num_correct_digits positions match the account number
  for (const auto& set : sets) {
    dcp::Lin matches;
    for (int i = 0; i < n; ++i) matches = matches + y[i][set.at(i).get<int>()];
    dcp::add_row(h, matches, k, k);
  }

  // the account number x: x[i] is the digit at position i
  std::vector<dcp::Lin> x(n);
  for (int i = 0; i < n; ++i)
    for (int v = 0; v < n; ++v) x[i] = x[i] + static_cast<double>(v) * y[i][v];
  out.add("x", x);
}
