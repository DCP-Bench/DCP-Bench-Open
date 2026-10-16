// Find a 10 digit number that uses each of the digits 0 to 9 exactly once, where the
// number formed by its first n digits is divisible by n, for n = 1..10. Output the number.
#include <cmath>
#include <vector>

#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  (void)instance;  // the problem has no instance data: 10 digits, fixed by the description
  const int digits = 10;

  // y[k][v] = 1 when the digit at position k (from the left, 0-based) has value v.
  std::vector<std::vector<dcp::Lin>> y(digits, std::vector<dcp::Lin>(10));
  for (int k = 0; k < digits; ++k)
    for (int v = 0; v < 10; ++v) y[k][v] = dcp::new_var(h, 0, 1);

  // d[k] is the digit at position k, tied to its one-hot indicators.
  std::vector<dcp::Lin> d(digits);
  for (int k = 0; k < digits; ++k) {
    d[k] = dcp::new_var(h, 0, 9);
    dcp::Lin value = d[k];
    for (int v = 0; v < 10; ++v) value = value - static_cast<double>(v) * y[k][v];
    dcp::add_row(h, value, 0, 0);  // the digit equals the value its indicator selects
    dcp::Lin one_value = y[k][0];
    for (int v = 1; v < 10; ++v) one_value = one_value + y[k][v];
    dcp::add_row(h, one_value, 1, 1);  // exactly one value per position
  }

  // Each digit 0 to 9 is used exactly once across the positions.
  for (int v = 0; v < 10; ++v) {
    dcp::Lin used = y[0][v];
    for (int k = 1; k < digits; ++k) used = used + y[k][v];
    dcp::add_row(h, used, 1, 1);
  }

  // A 10 digit number does not start with zero.
  dcp::add_row(h, d[0], 1, 9);

  // prefix_n is the number formed by the first n digits: prefix_n = 10 prefix_(n-1) + digit_n.
  // It is divisible by n: prefix_n = n q_n for an integer q_n.
  dcp::Lin previous = d[0];
  double upper = 0;  // largest prefix with n digits, 10^n - 1, built up digit by digit
  for (int n = 1; n <= digits; ++n) {
    upper = upper * 10 + 9;
    dcp::Lin prefix = dcp::new_var(h, 0, upper);
    if (n == 1) {
      dcp::add_row(h, prefix - d[0], 0, 0);  // the first digit is the prefix of length 1
    } else {
      dcp::add_row(h, prefix - 10.0 * previous - d[n - 1], 0, 0);  // append digit n
    }
    double quotient_upper = std::floor(upper / n);
    dcp::Lin quotient = dcp::new_var(h, 0, quotient_upper);
    dcp::add_row(h, prefix - static_cast<double>(n) * quotient, 0, 0);  // prefix divisible by n
    previous = prefix;
  }

  // The number itself: digit 0 is the most significant.
  dcp::Lin number = d[0];
  for (int k = 1; k < digits; ++k) number = 10.0 * number + d[k];
  out.add("number", number);
}
