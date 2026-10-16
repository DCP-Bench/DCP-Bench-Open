// Dudeney numbers: a positive integer larger than 1 that is a perfect cube whose
// digit sum equals its cube root. The instance gives n, the maximum number of digits.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int n = instance.at("n");

  // digits of the number, least significant first (leading zeros allowed)
  vec<IntVar*> digit;
  createVars(digit, n, 0, 9);

  // the number is built from its digits; it has at most n digits
  int max_number = 1;
  for (int i = 0; i < n; ++i) max_number *= 10;
  max_number -= 1;
  vec<int> place;
  int p = 1;
  for (int i = 0; i < n; ++i) { place.push(p); p *= 10; }
  IntVar* number = newIntVar(2, max_number);  // the number is larger than 1
  int_linear(place, digit, IRT_EQ, number);

  // the sum of the digits is the cube root of the number
  IntVar* root = newIntVar(1, 9 * n);
  int_linear(digit, IRT_EQ, root);

  // the number is a perfect cube: root * root * root = number
  IntVar* square = newIntVar(1, 81 * n * n);
  int_times(root, root, square);
  int_times(square, root, number);

  branch(digit, VAR_INORDER, VAL_MIN);

  outputs = {{"number", dcp::out(number)}};
}
