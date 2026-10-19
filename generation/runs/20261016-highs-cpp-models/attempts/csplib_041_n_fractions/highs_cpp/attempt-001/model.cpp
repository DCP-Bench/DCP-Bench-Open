// CSPLib 041, N-fractions: find distinct non-zero digits A, B, C, D, E, F, G, H, I
// such that A / BC + D / EF + G / HI = 1, where BC = 10B + C, EF = 10E + F and HI = 10H + I
// are two-digit numbers. The problem fixes the digits to 1..9; the instance has no data fields.
//
// Encoding: every digit is a one-hot group of binaries x[pos][v]. Every two-digit denominator is a
// one-hot choice z over the 72 two-digit numbers with distinct non-zero digits. The fraction
// A / BC is the sum over (a, p) of (a / p) * w, where w = [A = a] and [BC = p] is linearised with
// three rows per pair. The main equation is one row with right-hand side 1.
#include "dcp.h"

#include <vector>

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  (void)instance;  // the problem has no instance data; the digit range 1..9 is fixed by the statement

  enum Pos { A, B, C, D, E, F, G, H, I, NPOS };
  const char* names[NPOS] = {"A", "B", "C", "D", "E", "F", "G", "H", "I"};

  // Each of the nine digits takes exactly one value from 1 to 9.
  std::vector<std::vector<dcp::Lin>> x(NPOS, std::vector<dcp::Lin>(10));
  for (int p = 0; p < NPOS; ++p) {
    dcp::Lin one_value;
    for (int v = 1; v <= 9; ++v) {
      x[p][v] = dcp::new_var(h, 0, 1);
      one_value = one_value + x[p][v];
    }
    dcp::add_row(h, one_value, 1, 1);
  }

  // The nine digits are distinct: each value from 1 to 9 is used by exactly one digit.
  for (int v = 1; v <= 9; ++v) {
    dcp::Lin used_once;
    for (int p = 0; p < NPOS; ++p) used_once = used_once + x[p][v];
    dcp::add_row(h, used_once, 1, 1);
  }

  // Two-digit denominators: pairs (t, u) with t and u distinct and non-zero, so 10t + u.
  struct Denom {
    int value;
    int tens;
    int units;
  };
  std::vector<Denom> denoms;
  for (int t = 1; t <= 9; ++t)
    for (int u = 1; u <= 9; ++u)
      if (t != u) denoms.push_back({10 * t + u, t, u});

  // Denominator k is written with digits (tens pos, units pos) and numerator pos num.
  struct Fraction {
    Pos num;
    Pos tens;
    Pos units;
  };
  const Fraction fractions[3] = {{A, B, C}, {D, E, F}, {G, H, I}};

  dcp::Lin total;  // A / BC + D / EF + G / HI
  for (const Fraction& fr : fractions) {
    // Exactly one two-digit number is the denominator.
    std::vector<dcp::Lin> z(denoms.size());
    dcp::Lin one_denominator;
    for (std::size_t k = 0; k < denoms.size(); ++k) {
      z[k] = dcp::new_var(h, 0, 1);
      one_denominator = one_denominator + z[k];
    }
    dcp::add_row(h, one_denominator, 1, 1);

    // The tens digit of the denominator is the chosen tens digit of the number.
    for (int v = 1; v <= 9; ++v) {
      dcp::Lin tens_is_v;
      for (std::size_t k = 0; k < denoms.size(); ++k)
        if (denoms[k].tens == v) tens_is_v = tens_is_v + z[k];
      dcp::add_row(h, x[fr.tens][v] - tens_is_v, 0, 0);
    }

    // The units digit of the denominator is the chosen units digit of the number.
    for (int v = 1; v <= 9; ++v) {
      dcp::Lin units_is_v;
      for (std::size_t k = 0; k < denoms.size(); ++k)
        if (denoms[k].units == v) units_is_v = units_is_v + z[k];
      dcp::add_row(h, x[fr.units][v] - units_is_v, 0, 0);
    }

    // The fraction numerator digit times one over the chosen two-digit number.
    // w = [numerator = a] and [denominator = p], linearised for each pair (a, p) where a is not a digit of p.
    for (std::size_t k = 0; k < denoms.size(); ++k) {
      for (int a = 1; a <= 9; ++a) {
        if (a == denoms[k].tens || a == denoms[k].units) continue;
        dcp::Lin w = dcp::new_var(h, 0, 1);
        dcp::add_row(h, w - x[fr.num][a], -kHighsInf, 0);
        dcp::add_row(h, w - z[k], -kHighsInf, 0);
        dcp::add_row(h, w - x[fr.num][a] - z[k], -1, kHighsInf);
        total = total + (static_cast<double>(a) / denoms[k].value) * w;
      }
    }
  }

  // The equation A / BC + D / EF + G / HI = 1.
  dcp::add_row(h, total, 1, 1);

  // Declared outputs: the digit values, each read from its one-hot group.
  for (int p = 0; p < NPOS; ++p) {
    dcp::Lin digit;
    for (int v = 1; v <= 9; ++v) digit = digit + static_cast<double>(v) * x[p][v];
    out.add(names[p], digit);
  }
}
