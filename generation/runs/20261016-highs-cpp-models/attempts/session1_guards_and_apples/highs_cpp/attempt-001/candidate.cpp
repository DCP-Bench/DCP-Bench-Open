// A boy passes num_gates gates. At each gate he gives the guard half of his apples plus one,
// as an integer number of apples. After the last gate he has one apple, which he gives to the girl,
// leaving none. Output apples lists the number of apples before each gate, then the number after
// the last gate (num_gates + 1 values).
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const int gates = instance.at("num_gates").get<int>();

  // Apples before gate i, for i = 0..gates. Upper bound from the data: working back from one apple
  // left, the count before the first gate is 3 * 2^gates - 2, so 3 * 2^gates bounds every column.
  const double bound = 3.0 * std::pow(2.0, gates);
  std::vector<dcp::Lin> apples;
  for (int i = 0; i <= gates; ++i) apples.push_back(dcp::new_var(h, 0, bound));

  // After the last gate he has exactly one apple left, which he gives to the girl.
  dcp::add_row(h, apples[gates], 1, 1);

  // At each gate the guard takes half of the apples plus one, so the apples before the gate are
  // even and the apples after it are half of them minus one: a_i = 2 * a_{i+1} + 2.
  for (int i = 0; i < gates; ++i)
    dcp::add_row(h, apples[i] - 2 * apples[i + 1], 2, 2);

  out.add("apples", apples);
}
