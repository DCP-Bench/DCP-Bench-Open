#include "dcp.h"

// Langford's number problem: two copies of each number 1..k are arranged in one
// sequence of 2k positions so that the two i's are i+1 positions apart.
class Langford : public dcp::Space {
 protected:
  IntVarArray sol;  // sol[p]: the number at position p of the sequence
  IntVarArray pos;  // pos[2(i-1)] and pos[2(i-1)+1]: the two positions of number i

 public:
  explicit Langford(const json& instance) {
    int k = instance.at("k").get<int>();
    int n = 2 * k;
    sol = IntVarArray(*this, n, 1, k);
    pos = IntVarArray(*this, n, 0, n - 1);

    IntVarArgs x;
    for (int p = 0; p < n; ++p) x << sol[p];

    // the 2k numbers occupy the 2k positions, each position holds one number
    distinct(*this, pos, IPL_DOM);

    for (int i = 1; i <= k; ++i) {
      int a = 2 * (i - 1);
      int b = a + 1;
      // the two i's appear i+1 numbers apart
      rel(*this, pos[b] == pos[a] + i + 1);
      // the number at each of the two positions of i is i
      IntVar value(*this, i, i);
      element(*this, x, pos[a], value);
      element(*this, x, pos[b], value);
    }

    // branch on the positions of the numbers, then read off the sequence
    branch(*this, pos, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    branch(*this, sol, INT_VAR_NONE(), INT_VAL_MIN());
    output("sol", sol);
  }

  Langford(Langford& s) : dcp::Space(s) {
    sol.update(*this, s.sol);
    pos.update(*this, s.pos);
  }
  Gecode::Space* copy() override { return new Langford(*this); }
};

DCP_MODEL(Langford)
