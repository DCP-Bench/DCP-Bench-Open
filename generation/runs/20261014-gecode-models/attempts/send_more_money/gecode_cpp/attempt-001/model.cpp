#include "dcp.h"

// Send More Money: assign each letter of SEND + MORE = MONEY a digit so that
// the sum holds. Each letter is a different digit 0..9, and the first letter
// of each word is not zero. The instance has no fields; the puzzle is fixed.

class SendMoreMoney : public dcp::Space {
 protected:
  // l[k] is the digit of the letter with index k: S, E, N, D, M, O, R, Y.
  IntVarArray l;

  static constexpr int S = 0, E = 1, N = 2, D = 3, M = 4, O = 5, R = 6, Y = 7;

 public:
  explicit SendMoreMoney(const json& instance) {
    (void)instance;  // no instance fields
    l = IntVarArray(*this, 8, 0, 9);

    // each letter stands for a unique digit
    distinct(*this, l, IPL_DOM);

    // the first letter of SEND and of MORE cannot be zero
    rel(*this, l[S], IRT_NQ, 0);
    rel(*this, l[M], IRT_NQ, 0);

    // SEND + MORE = MONEY, collected per letter:
    // 1000 S + 91 E - 90 N + D - 9000 M - 900 O + 10 R - Y = 0
    IntVarArgs x;
    for (int k = 0; k < 8; ++k) x << l[k];
    IntArgs w({1000, 91, -90, 1, -9000, -900, 10, -1});
    linear(*this, w, x, IRT_EQ, 0);

    // branch on the letters in order, smallest digit first
    branch(*this, l, INT_VAR_SIZE_MIN(), INT_VAL_MIN());

    output("s", l[S]);
    output("e", l[E]);
    output("n", l[N]);
    output("d", l[D]);
    output("m", l[M]);
    output("o", l[O]);
    output("r", l[R]);
    output("y", l[Y]);
  }

  SendMoreMoney(SendMoreMoney& s) : dcp::Space(s) { l.update(*this, s.l); }

  Gecode::Space* copy() override { return new SendMoreMoney(*this); }
};

DCP_MODEL(SendMoreMoney)
