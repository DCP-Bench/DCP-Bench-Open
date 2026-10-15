#include "dcp.h"

// Guards and apples: a boy wants to give an apple to a girl beyond num_gates gates. At
// each gate the guard takes half of his apples plus one, and the boy gives an integer
// number of apples (so his count before each gate is even). He keeps one apple for the
// girl, and after giving it he has no apples left.
// Output apples: the count before each gate, then the count after the last gate.
class GuardsAndApples : public dcp::Space {
 protected:
  IntVarArray apples;  // apples[i]: apples before gate i; apples[n]: after the last gate
  IntVarArray bribe;   // bribe[i]: apples given to the guard at gate i (auxiliary)

 public:
  explicit GuardsAndApples(const json& instance) {
    int n = instance.at("num_gates").get<int>();

    // Upper bound: the reverse recurrence from one apple (a_i = 2 * (a_{i+1} + 1))
    // gives 3 * 2^n - 2 apples at the start, and the count never grows along the way.
    long long top = 3LL * (1LL << n) - 2;
    int hi = static_cast<int>(top);

    apples = IntVarArray(*this, n + 1, 0, hi);
    bribe = IntVarArray(*this, n, 1, hi / 2 + 1);

    // one apple is left after the last gate: the girl gets it, and nothing remains
    rel(*this, apples[n] == 1);

    for (int i = 0; i < n; ++i) {
      // the bribe is half of the apples plus one, and must be a whole number:
      // 2 * bribe = apples + 2
      IntVarArgs bribe_eq;
      bribe_eq << bribe[i] << apples[i];
      linear(*this, IntArgs({2, -1}), bribe_eq, IRT_EQ, 2);

      // after the guard the boy has the apples he had minus the bribe
      IntVarArgs left;
      left << apples[i + 1] << apples[i] << bribe[i];
      linear(*this, IntArgs({1, -1, 1}), left, IRT_EQ, 0);
    }

    // branch on the apple counts first, then on the bribes
    branch(*this, apples, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    branch(*this, bribe, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    output("apples", apples);
  }

  GuardsAndApples(GuardsAndApples& s) : dcp::Space(s) {
    apples.update(*this, s.apples);
    bribe.update(*this, s.bribe);
  }
  Gecode::Space* copy() override { return new GuardsAndApples(*this); }
};

DCP_MODEL(GuardsAndApples)
