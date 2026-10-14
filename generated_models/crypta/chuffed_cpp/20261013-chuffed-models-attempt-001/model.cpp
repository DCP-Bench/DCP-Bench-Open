// Cryptarithmetic puzzle: top + bottom = result, with distinct digits for the letters A..J and no leading zero.
#include "dcp.h"
#include <map>
#include <string>

void Build(const json& instance, json& outputs) {
  // The three numbers are fixed by the problem statement (most significant digit first).
  const std::string top = "BAIJJAJIIAHFCFEBBJEA";
  const std::string bottom = "DHFGABCDIDBIFFAGFEJE";
  const std::string result = "GJEGACDDHFAFJBFIHEEF";
  const int len = 20;
  const int letters = 10;

  // digit[k] is the digit of the letter 'A' + k
  vec<IntVar*> digit;
  createVars(digit, letters, 0, 9, true);

  // all letters are distinct digits from 0 to 9
  all_different(digit);

  // the first letter of each number cannot be zero
  int_rel(digit[top[0] - 'A'], IRT_NE, 0);
  int_rel(digit[bottom[0] - 'A'], IRT_NE, 0);
  int_rel(digit[result[0] - 'A'], IRT_NE, 0);

  // column addition from the least significant digit: top + bottom + carry in = result + 10 * carry out.
  // carry[i] is the carry into column i (column 0 is the units); there is no carry out of the last column.
  vec<IntVar*> carry;
  createVars(carry, len + 1, 0, 1, true);
  int_rel(carry[0], IRT_EQ, 0);
  int_rel(carry[len], IRT_EQ, 0);
  for (int i = 0; i < len; ++i) {
    int pos = len - 1 - i;
    // coefficient per letter (a letter may occur more than once in a column)
    std::map<int, int> coef;
    coef[top[pos] - 'A'] += 1;
    coef[bottom[pos] - 'A'] += 1;
    coef[result[pos] - 'A'] -= 1;
    vec<int> a;
    vec<IntVar*> v;
    for (auto& kv : coef)
      if (kv.second != 0) {
        a.push(kv.second);
        v.push(digit[kv.first]);
      }
    a.push(1);
    v.push(carry[i]);
    a.push(-10);
    v.push(carry[i + 1]);
    int_linear(a, v, IRT_EQ, 0);
  }

  branch(digit, VAR_SIZE_MIN, VAL_MIN);
  json out = json::object();
  for (int k = 0; k < letters; ++k) out[std::string(1, 'A' + k)] = dcp::out(digit[k]);
  outputs = out;
}
