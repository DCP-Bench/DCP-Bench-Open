#include "dcp.h"

// Divisible by 1 through 9: find a 10 digit number that uses each of the digits
// 0 to 9 exactly once, where the number formed by its first n digits is divisible
// by n, for n from 1 to 10.
class DivisibleByOneThroughNine : public dcp::Space {
 protected:
  IntVarArray digit;   // digit[i]: the (i+1)-th digit of the number, read from the left
  IntVarArray prefix;  // prefix[n-1]: the number formed by its first n digits
  IntVarArray quot;    // quot[n-1]: prefix[n-1] / n, the quotient when n divides it

 public:
  explicit DivisibleByOneThroughNine(const json& instance) {
    (void)instance;  // the problem has no instance data
    digit = IntVarArray(*this, 10, 0, 9);
    // a prefix of up to 9 digits is below 10^9, which fits an IntVar
    prefix = IntVarArray(*this, 9, 0, 999999999);
    quot = IntVarArray(*this, 9, 0, 999999999);

    // the number uses each of the digits 0 to 9 exactly once
    distinct(*this, digit, IPL_DOM);

    // the number has 10 digits, so its first digit is not 0
    rel(*this, digit[0] != 0);

    for (int n = 1; n <= 9; ++n) {
      // the number formed by the first n digits: the first n-1 digits shifted
      // one place left, followed by digit n
      if (n == 1)
        rel(*this, prefix[0] == digit[0]);
      else
        rel(*this, prefix[n - 1] == 10 * prefix[n - 2] + digit[n - 1]);

      // the first n digits form a number divisible by n (every number is
      // divisible by 1, so the n = 1 case is only the link above)
      if (n > 1) rel(*this, prefix[n - 1] == n * quot[n - 1]);
    }

    // the whole number (10 digits) is divisible by 10. It equals 10 times the
    // first 9 digits plus the 10th digit, so it is divisible by 10 exactly when
    // the 10th digit is 0 (derived here, not a Gecode global)
    rel(*this, digit[9] == 0);

    // branch on the digits from the left, so each divisibility check prunes
    // as soon as its prefix is fixed
    branch(*this, digit, INT_VAR_NONE(), INT_VAL_MIN());
    branch(*this, prefix, INT_VAR_NONE(), INT_VAL_MIN());
    branch(*this, quot, INT_VAR_NONE(), INT_VAL_MIN());

    IntVarArgs number;
    for (int i = 0; i < 10; ++i) number << digit[i];
    output_digits("number", number, 10);
  }

  DivisibleByOneThroughNine(DivisibleByOneThroughNine& s) : dcp::Space(s) {
    digit.update(*this, s.digit);
    prefix.update(*this, s.prefix);
    quot.update(*this, s.quot);
  }
  Gecode::Space* copy() override { return new DivisibleByOneThroughNine(*this); }
};

DCP_MODEL(DivisibleByOneThroughNine)
