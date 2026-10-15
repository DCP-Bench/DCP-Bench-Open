#include "dcp.h"

// Five statements, each claiming how many of the five statements are false:
// statement i says "exactly i of these statements are false" (i = 1..5).
// Decide which statements are true. The instance carries no data.
class FiveStatements : public dcp::Space {
 protected:
  BoolVarArray s;  // s[i-1]: statement i is true
  IntVar total;    // number of true statements

 public:
  explicit FiveStatements(const json& instance) {
    (void)instance;
    const int n = 5;
    s = BoolVarArray(*this, n, 0, 1);
    total = expr(*this, sum(s));

    // statement i is true exactly when the number of false statements is i,
    // i.e. when the number of true statements is 5 - i
    for (int i = 1; i <= n; ++i) {
      BoolVar exactly_i_false = expr(*this, total == n - i);
      rel(*this, s[i - 1] == exactly_i_false);
    }

    branch(*this, s, BOOL_VAR_NONE(), BOOL_VAL_MIN());
    output("statements", s);
  }

  FiveStatements(FiveStatements& sp) : dcp::Space(sp) {
    s.update(*this, sp.s);
    total.update(*this, sp.total);
  }
  Gecode::Space* copy() override { return new FiveStatements(*this); }
};

DCP_MODEL(FiveStatements)
