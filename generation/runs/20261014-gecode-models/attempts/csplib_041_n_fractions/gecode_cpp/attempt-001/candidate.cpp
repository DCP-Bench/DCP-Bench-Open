#include "dcp.h"

// N fractions: find nine distinct non-zero digits A..I such that
// A/BC + D/EF + G/HI = 1, where BC, EF and HI are the two-digit numbers
// 10*B + C, 10*E + F and 10*H + I.
class NFractions : public dcp::Space {
 protected:
  IntVarArray d;  // d[0..8] = A, B, C, D, E, F, G, H, I
 public:
  explicit NFractions(const json& instance) {
    (void)instance;  // the problem has no instance fields
    d = IntVarArray(*this, 9, 1, 9);
    IntVar A = d[0], B = d[1], C = d[2], D = d[3], E = d[4],
           F = d[5], G = d[6], H = d[7], I = d[8];

    // the nine digits are distinct non-zero digits
    distinct(*this, d, IPL_DOM);

    // BC, EF and HI are two-digit numbers
    IntVar BC = expr(*this, 10 * B + C);
    IntVar EF = expr(*this, 10 * E + F);
    IntVar HI = expr(*this, 10 * H + I);

    // A/BC + D/EF + G/HI = 1, multiplied through by BC*EF*HI:
    // A*EF*HI + D*BC*HI + G*BC*EF = BC*EF*HI
    IntVar EFHI = expr(*this, EF * HI);
    IntVar BCHI = expr(*this, BC * HI);
    IntVar BCEF = expr(*this, BC * EF);
    IntVar BCEFHI = expr(*this, BC * EFHI);
    IntVar termA = expr(*this, A * EFHI);
    IntVar termD = expr(*this, D * BCHI);
    IntVar termG = expr(*this, G * BCEF);
    rel(*this, termA + termD + termG == BCEFHI);

    branch(*this, d, INT_VAR_SIZE_MIN(), INT_VAL_MIN());

    output("A", d[0]);
    output("B", d[1]);
    output("C", d[2]);
    output("D", d[3]);
    output("E", d[4]);
    output("F", d[5]);
    output("G", d[6]);
    output("H", d[7]);
    output("I", d[8]);
  }

  NFractions(NFractions& s) : dcp::Space(s) { d.update(*this, s.d); }
  Gecode::Space* copy() override { return new NFractions(*this); }
};

DCP_MODEL(NFractions)
