// Send More Money: assign digits to the letters s, e, n, d, m, o, r, y so that
// SEND + MORE = MONEY holds. Each letter is one digit from 0 to 9, each letter
// takes a different digit, and the first letter of each word (s and m) is not zero.
// The puzzle has no data, so the instance is not read.
#include "dcp.h"

void build(const json&, Highs& h, dcp::Outputs& out) {
  const int letters = 8;  // order: s e n d m o r y
  const int digits = 10;
  enum { S, E, N, D, M, O, R, Y };

  // Digit of each letter: an integer column in 0..9.
  std::vector<dcp::Lin> x;
  for (int l = 0; l < letters; ++l) x.push_back(dcp::new_var(h, 0, digits - 1));

  // pick[l][v] = 1 when letter l takes digit v.
  std::vector<std::vector<dcp::Lin>> pick(letters, std::vector<dcp::Lin>(digits));
  for (int l = 0; l < letters; ++l)
    for (int v = 0; v < digits; ++v) pick[l][v] = dcp::new_var(h, 0, 1);

  // the first letter of each word cannot be zero: s and m take no digit 0
  dcp::add_row(h, pick[S][0], 0, 0);
  dcp::add_row(h, pick[M][0], 0, 0);

  // each letter represents exactly one digit, and the digit is its value
  for (int l = 0; l < letters; ++l) {
    dcp::Lin one = 0;
    dcp::Lin value = x[l];
    for (int v = 0; v < digits; ++v) {
      one = one + pick[l][v];
      value = value - static_cast<double>(v) * pick[l][v];
    }
    dcp::add_row(h, one, 1, 1);
    dcp::add_row(h, value, 0, 0);
  }

  // each letter represents a unique digit: every digit is used by at most one letter
  for (int v = 0; v < digits; ++v) {
    dcp::Lin used = 0;
    for (int l = 0; l < letters; ++l) used = used + pick[l][v];
    dcp::add_row(h, used, -kHighsInf, 1);
  }

  // SEND + MORE = MONEY
  dcp::Lin send = 1000.0 * x[S] + 100.0 * x[E] + 10.0 * x[N] + x[D];
  dcp::Lin more = 1000.0 * x[M] + 100.0 * x[O] + 10.0 * x[R] + x[E];
  dcp::Lin money = 10000.0 * x[M] + 1000.0 * x[O] + 100.0 * x[N] + 10.0 * x[E] + x[Y];
  dcp::add_row(h, send + more - money, 0, 0);

  // satisfaction problem: no objective
  out.add("d", x[D]);
  out.add("e", x[E]);
  out.add("m", x[M]);
  out.add("n", x[N]);
  out.add("o", x[O]);
  out.add("r", x[R]);
  out.add("s", x[S]);
  out.add("y", x[Y]);
}
