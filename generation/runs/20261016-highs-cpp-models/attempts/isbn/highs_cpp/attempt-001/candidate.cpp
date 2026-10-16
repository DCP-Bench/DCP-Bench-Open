// ISBN-13 validation and check digit calculation. Given 13 digits where -1 marks an
// unknown digit, find the unknown digits so that the number is a valid ISBN-13.
// The number must start with 978 or 979. The check digit is the one that makes the
// weighted digit sum a multiple of 10, with weights 1 and 3 alternating from the first digit.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  std::vector<int> init = instance.at("isbn_init").get<std::vector<int>>();
  const int n = static_cast<int>(init.size());

  // each digit is a whole number from 0 to 9; a given digit is fixed to its value
  std::vector<dcp::Lin> digit;
  for (int i = 0; i < n; ++i) {
    if (init[i] == -1) {
      digit.push_back(dcp::new_var(h, 0, 9));
    } else {
      digit.push_back(dcp::new_var(h, init[i], init[i]));
    }
  }

  // the number starts with 978 or 979: the first digit is 9, the second is 7,
  // and the third is 8 or 9 (a binary chooses between them)
  dcp::Lin third_is_9 = dcp::new_var(h, 0, 1);
  dcp::add_row(h, digit[0], 9, 9);
  dcp::add_row(h, digit[1], 7, 7);
  dcp::add_row(h, digit[2] - third_is_9, 8, 8);

  // the weighted digit sum, weights 1 and 3 alternating, is a multiple of 10
  dcp::Lin weighted;
  int max_sum = 0;
  for (int i = 0; i < n; ++i) {
    int weight = (i % 2 == 0) ? 1 : 3;
    weighted = weighted + weight * digit[i];
    max_sum += weight * 9;
  }
  dcp::Lin groups = dcp::new_var(h, 0, max_sum / 10);
  dcp::add_row(h, weighted - 10 * groups, 0, 0);

  out.add("isbn", digit);
}
