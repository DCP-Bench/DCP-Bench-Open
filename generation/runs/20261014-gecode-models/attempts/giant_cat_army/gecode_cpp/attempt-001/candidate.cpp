#include "dcp.h"

// Giant cat army: start from the list [0] and build a list of integers by adding 5,
// adding 7, or taking the square root (only when the result is an integer). The
// list has 24 entries, ends with 14, has all entries distinct and at most 60, and
// contains 2, 10 and 14 in that order (other numbers may lie between them).
class GiantCatArmy : public dcp::Space {
 protected:
  IntVarArray x;       // x[i]: the i-th entry of the list
  BoolVarArray seen2;  // seen2[i]: the value 2 is among x[0..i]

 public:
  GiantCatArmy(const json& instance) {
    (void)instance;  // the problem has no instance data; the sizes are fixed by the description
    const int len = 24;    // length of the list
    const int maxv = 60;   // every entry is at most 60

    x = IntVarArray(*this, len, 0, maxv);
    seen2 = BoolVarArray(*this, len, 0, 1);

    // the list starts with 0 and ends with 14
    rel(*this, x[0] == 0);
    rel(*this, x[len - 1] == 14);

    // all elements are distinct
    distinct(*this, x, IPL_DOM);

    // each step adds 5, adds 7, or takes the square root of the previous entry;
    // the table lists the allowed pairs (previous, next)
    TupleSet steps(2);
    for (int a = 0; a <= maxv; ++a) {
      if (a + 5 <= maxv) steps.add(IntArgs({a, a + 5}));  // add 5
      if (a + 7 <= maxv) steps.add(IntArgs({a, a + 7}));  // add 7
    }
    for (int s = 0; s * s <= maxv; ++s) steps.add(IntArgs({s * s, s}));  // square root
    steps.finalize();
    for (int i = 0; i + 1 < len; ++i) extensional(*this, x.slice(i, 1, 2), steps);

    // the list contains 2, 10 and 14 in that order:
    // 2 occurs somewhere in the list, and 10 occurs once, after the first 2
    rel(*this, seen2[0] == (x[0] == 2));
    for (int i = 1; i < len; ++i) rel(*this, seen2[i] == (seen2[i - 1] || (x[i] == 2)));
    rel(*this, seen2[len - 1] == 1);
    count(*this, x, 10, IRT_EQ, 1);
    for (int i = 1; i < len; ++i) rel(*this, (x[i] == 10) >> (seen2[i - 1] == 1));

    // 14 is the last entry, so 10 comes before it

    branch(*this, x, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    branch(*this, seen2, BOOL_VAR_NONE(), BOOL_VAL_MIN());
    output("x", x);
  }

  GiantCatArmy(GiantCatArmy& s) : dcp::Space(s) {
    x.update(*this, s.x);
    seen2.update(*this, s.seen2);
  }

  Gecode::Space* copy() override { return new GiantCatArmy(*this); }
};

DCP_MODEL(GiantCatArmy)
