#include "dcp.h"

// Ten-digit number that uses each of the digits 0 to 9 exactly once, where the
// number formed by its first n digits is divisible by n for every n.
class DivisibleByOneThroughNine : public dcp::Space {
 protected:
  IntVarArray d;    // d[i]: the digit at position i (read from the left)
  IntVar number;    // the ten-digit number

 public:
  explicit DivisibleByOneThroughNine(const json& instance) {
    (void)instance;  // the problem has no instance data; every constant is in the statement
    d = IntVarArray(*this, 10, 0, 9);

    // the digits 0 to 9 each appear exactly once
    distinct(*this, d, IPL_DOM);

    // a ten-digit number does not start with zero
    rel(*this, d[0] != 0);

    // the first n digits form a number divisible by n, for n = 1 to 9
    IntVar prefix = d[0];  // the first digit, a number divisible by 1
    for (int n = 2; n <= 9; ++n) {
      // the first n digits: the first n-1 digits shifted one place, plus digit n
      IntVar next(*this, 0, static_cast<int>(std::pow(10, n)) - 1);
      rel(*this, next == 10 * prefix + d[n - 1]);
      // the number formed by the first n digits is a multiple of n
      IntVar quotient(*this, 0, (static_cast<int>(std::pow(10, n)) - 1) / n);
      rel(*this, next == n * quotient);
      prefix = next;
    }

    // the whole number is divisible by 10, so its last digit is zero
    rel(*this, d[9] == 0);

    // the number itself: the digits weighted by their place value
    IntArgs place(10);
    for (int i = 0; i < 10; ++i) place[i] = static_cast<int>(std::pow(10, 9 - i));
    number = expr(*this, sum(place, d));

    branch(*this, d, INT_VAR_NONE(), INT_VAL_MIN());
    output("number", number);
  }

  DivisibleByOneThroughNine(DivisibleByOneThroughNine& s) : dcp::Space(s) {
    d.update(*this, s.d);
    number.update(*this, s.number);
  }
  Gecode::Space* copy() override { return new DivisibleByOneThroughNine(*this); }
};

DCP_MODEL(DivisibleByOneThroughNine)
