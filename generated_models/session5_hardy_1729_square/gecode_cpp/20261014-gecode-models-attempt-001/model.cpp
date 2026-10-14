#include "dcp.h"

// Hardy's square problem: four different numbers a, b, c, d in 1..100 with
// a^2 + b^2 = c^2 + d^2. The instance carries no fields, so the constants come
// from the problem statement (the range 1..100).
class HardySquare : public dcp::Space {
 protected:
  IntVar a, b, c, d;     // the four numbers
  IntVar sa, sb, sc, sd; // their squares

 public:
  explicit HardySquare(const json& instance) {
    (void)instance;

    // four numbers between 1 and 100
    a = IntVar(*this, 1, 100);
    b = IntVar(*this, 1, 100);
    c = IntVar(*this, 1, 100);
    d = IntVar(*this, 1, 100);

    // a, b, c and d are all different
    IntVarArgs nums;
    nums << a << b << c << d;
    distinct(*this, nums, IPL_DOM);

    // squares of the four numbers (the largest is 100^2 = 10000)
    sa = IntVar(*this, 1, 10000);
    sb = IntVar(*this, 1, 10000);
    sc = IntVar(*this, 1, 10000);
    sd = IntVar(*this, 1, 10000);
    sqr(*this, a, sa);
    sqr(*this, b, sb);
    sqr(*this, c, sc);
    sqr(*this, d, sd);

    // the sum of the squares of the first two equals the sum of the squares of the other two
    rel(*this, sa + sb == sc + sd);

    // branch on the four numbers; their squares follow from them
    branch(*this, nums, INT_VAR_SIZE_MIN(), INT_VAL_MIN());

    output("a", a);
    output("b", b);
    output("c", c);
    output("d", d);
  }

  HardySquare(HardySquare& s) : dcp::Space(s) {
    a.update(*this, s.a);
    b.update(*this, s.b);
    c.update(*this, s.c);
    d.update(*this, s.d);
    sa.update(*this, s.sa);
    sb.update(*this, s.sb);
    sc.update(*this, s.sc);
    sd.update(*this, s.sd);
  }

  Gecode::Space* copy() override { return new HardySquare(*this); }
};

DCP_MODEL(HardySquare)
