#include "dcp.h"

// Age changing: find my age m and my husband's age h (non-negative integers).
// Starting from my age and applying the four operations +2, /8, -3, *7, each once
// and in some order, gives his age h. Starting from his age and applying the same
// four operations in a different order gives my age m.
class AgeChanging : public dcp::Space {
 protected:
  // Bound on every age in the chains. The solutions are far below it; the bound
  // only makes the domains finite.
  static constexpr int MAX_AGE = 2000;

  IntVarArray mine;  // mine[0] = m; mine[k] = age after k operations from my age; mine[4] = h
  IntVarArray his;   // his[0] = h; his[k] = age after k operations from his age; his[4] = m
  IntVarArray ops1;  // ops1[k]: operation applied at step k from my age (0 +2, 1 /8, 2 -3, 3 *7)
  IntVarArray ops2;  // ops2[k]: operation applied at step k from his age

 public:
  explicit AgeChanging(const json& /*instance*/) {
    // Operation table: (operation, age before, age after). Each operation is a
    // function of the age: +2, exact division by 8 (only for multiples of 8),
    // -3 (never below 0), *7. Ages above MAX_AGE are not allowed.
    TupleSet step(3);
    for (int x = 0; x <= MAX_AGE; ++x) {
      if (x + 2 <= MAX_AGE) step.add(IntArgs({0, x, x + 2}));
      if (x % 8 == 0) step.add(IntArgs({1, x, x / 8}));
      if (x >= 3) step.add(IntArgs({2, x, x - 3}));
      if (7 * x <= MAX_AGE) step.add(IntArgs({3, x, 7 * x}));
    }
    step.finalize();

    mine = IntVarArray(*this, 5, 0, MAX_AGE);
    his = IntVarArray(*this, 5, 0, MAX_AGE);
    ops1 = IntVarArray(*this, 4, 0, 3);
    ops2 = IntVarArray(*this, 4, 0, 3);

    // each operation is used exactly once in each sequence
    distinct(*this, ops1, IPL_DOM);
    distinct(*this, ops2, IPL_DOM);

    // applying the chosen operation to the age at each step gives the next age
    for (int k = 0; k < 4; ++k) {
      IntVarArgs t1;
      t1 << ops1[k] << mine[k] << mine[k + 1];
      extensional(*this, t1, step);
      IntVarArgs t2;
      t2 << ops2[k] << his[k] << his[k + 1];
      extensional(*this, t2, step);
    }

    // starting from my age the result is his age, and from his age the result is my age
    rel(*this, his[0], IRT_EQ, mine[4]);
    rel(*this, his[4], IRT_EQ, mine[0]);

    // the second sequence is in a different order: at least one step differs
    BoolVarArgs differs;
    for (int k = 0; k < 4; ++k) differs << expr(*this, ops1[k] != ops2[k]);
    linear(*this, differs, IRT_GQ, 1);

    branch(*this, ops1, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    branch(*this, ops2, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    branch(*this, mine, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    branch(*this, his, INT_VAR_SIZE_MIN(), INT_VAL_MIN());

    output("m", mine[0]);
    output("h", mine[4]);
  }

  AgeChanging(AgeChanging& s) : dcp::Space(s) {
    mine.update(*this, s.mine);
    his.update(*this, s.his);
    ops1.update(*this, s.ops1);
    ops2.update(*this, s.ops2);
  }
  Gecode::Space* copy() override { return new AgeChanging(*this); }
};

DCP_MODEL(AgeChanging)
