// ISBN-13: fill in the unknown digits (-1) of a 13-digit ISBN so that its check digit is correct
// and it starts with 978 or 979.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  std::vector<int> isbn_init = instance.at("isbn_init").get<std::vector<int>>();

  // isbn[i] = i-th digit
  vec<IntVar*> isbn;
  createVars(isbn, 13, 0, 9);

  // known digits keep their value; -1 marks an unknown digit
  for (int i = 0; i < 13; ++i) {
    if (isbn_init[i] != -1) int_rel(isbn[i], IRT_EQ, isbn_init[i]);
  }

  // an ISBN-13 must start with 978 or 979
  int_rel(isbn[0], IRT_EQ, 9);
  int_rel(isbn[1], IRT_EQ, 7);
  int_rel(isbn[2], IRT_GE, 8);

  // the first 12 digits are multiplied alternately by 1 and 3 (starting with 1) and summed;
  // the check digit is (10 - (sum % 10)) % 10, i.e. the weighted sum plus the check digit is a
  // multiple of 10. The sum is at most 9 * 3 * 6 + 9 * 6 = 216 so the multiple is at most 22.
  vec<int> weight;
  vec<IntVar*> digits;
  for (int i = 0; i < 12; ++i) {
    weight.push(i % 2 == 0 ? 1 : 3);
    digits.push(isbn[i]);
  }
  weight.push(1);
  digits.push(isbn[12]);
  IntVar* tens = newIntVar(0, 23);
  weight.push(-10);
  digits.push(tens);
  int_linear(weight, digits, IRT_EQ, 0);

  branch(isbn, VAR_INORDER, VAL_MIN);

  json out = json::array();
  for (int i = 0; i < 13; ++i) out.push_back(dcp::out(isbn[i]));
  outputs = {{"isbn", out}};
}
