// de Bruijn sequence: a cyclic sequence over an alphabet of size base in which every string of length n occurs exactly once.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int base = instance.at("base");
  int n = instance.at("n");

  // a de Bruijn sequence has base^n symbols, one for each string of length n
  int len = 1;
  for (int i = 0; i < n; ++i) len *= base;

  // seq[i] is the i-th symbol of the sequence, a value in 0..base-1
  vec<IntVar*> seq;
  createVars(seq, len, 0, base - 1, true);

  // weight of the symbol at position j of a window: base^(n-1-j), so a window reads as a base-"base" number
  vec<int> weight;
  int power = 1;
  std::vector<int> weights_rev;
  for (int j = 0; j < n; ++j) {
    weights_rev.push_back(power);
    power *= base;
  }
  for (int j = n - 1; j >= 0; --j) weight.push(weights_rev[j]);

  // window[i] is the string of length n that starts at position i, read cyclically, as a number
  vec<IntVar*> window;
  createVars(window, len, 0, len - 1);
  for (int i = 0; i < len; ++i) {
    vec<IntVar*> symbols;
    for (int j = 0; j < n; ++j) symbols.push(seq[(i + j) % len]);
    // window i is the number formed by the n symbols starting at position i
    int_linear(weight, symbols, IRT_EQ, window[i]);
  }

  // every length-n string occurs exactly once, so all windows are different
  all_different(window);

  // search on the symbols in sequence order
  branch(seq, VAR_INORDER, VAL_MIN);

  json de_bruijn = json::array();
  for (int i = 0; i < len; ++i) de_bruijn.push_back(dcp::out(seq[i]));
  outputs = {{"de_bruijn", de_bruijn}};
}
