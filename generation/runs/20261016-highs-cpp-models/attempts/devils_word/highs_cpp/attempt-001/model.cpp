// Devil's word: insert '+' or '-' before each integer of the array arr so that
// summing them gives total. Output result is the array with the signs applied.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  std::vector<int> arr = instance.at("arr").get<std::vector<int>>();
  int total = instance.at("total").get<int>();
  std::size_t n = arr.size();

  // each integer gets a sign: the binary column is 1 for '+' and 0 for '-'
  std::vector<dcp::Lin> result;
  dcp::Lin sum;
  for (std::size_t i = 0; i < n; i++) {
    dcp::Lin plus = dcp::new_var(h, 0, 1);
    // the signed integer is +arr[i] when plus is 1 and -arr[i] when plus is 0
    double a = arr[i];
    dcp::Lin signed_value = (2.0 * a) * plus - a;
    result.push_back(signed_value);
    sum = sum + signed_value;
  }

  // the signed integers sum to the total
  dcp::add_row(h, sum, total, total);

  out.add("result", result);
}
