#include "dcp.h"

// Bank card PIN: find the 4-digit PIN abcd such that no two digits are the same,
// the 2-digit number cd is 3 times the 2-digit number ab, and the 2-digit number
// da is 2 times the 2-digit number bc. Print the PIN as (a, b, c, d).
class BankCardPin : public dcp::Space {
 protected:
  IntVarArray p;  // p[0..3] = a, b, c, d; each is a decimal digit

 public:
  explicit BankCardPin(const json& instance) : p(*this, 4, 0, 9) {
    (void)instance;  // the problem has no instance data

    // no two digits are the same
    distinct(*this, p, IPL_DOM);

    // the 2-digit number cd is 3 times the 2-digit number ab: 10c + d = 3(10a + b)
    IntVarArgs cd_ab;
    cd_ab << p[2] << p[3] << p[0] << p[1];
    linear(*this, IntArgs({10, 1, -30, -3}), cd_ab, IRT_EQ, 0);

    // the 2-digit number da is 2 times the 2-digit number bc: 10d + a = 2(10b + c)
    IntVarArgs da_bc;
    da_bc << p[3] << p[0] << p[1] << p[2];
    linear(*this, IntArgs({10, 1, -20, -2}), da_bc, IRT_EQ, 0);

    branch(*this, p, INT_VAR_SIZE_MIN(), INT_VAL_MIN());

    output("a", p[0]);
    output("b", p[1]);
    output("c", p[2]);
    output("d", p[3]);
  }

  BankCardPin(BankCardPin& s) : dcp::Space(s) { p.update(*this, s.p); }
  Gecode::Space* copy() override { return new BankCardPin(*this); }
};

DCP_MODEL(BankCardPin)
