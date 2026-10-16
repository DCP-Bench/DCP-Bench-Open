#include "dcp.h"

// Mr Greenguest's dress party: choose which green items to wear (tie t, hat h,
// shirt r, socks s) and whether to pay the entrance fee n, at minimum total cost.
// The instance has no fields; the prices and the fee come from the description.
class FancyDress : public dcp::Space {
 protected:
  BoolVar t, h, r, s, n;
  IntVar cost;

 public:
  explicit FancyDress(const json& instance) {
    (void)instance;
    t = BoolVar(*this, 0, 1);  // green tie
    h = BoolVar(*this, 0, 1);  // green hat (used)
    r = BoolVar(*this, 0, 1);  // green shirt (owned)
    s = BoolVar(*this, 0, 1);  // green socks
    n = BoolVar(*this, 0, 1);  // pays the 11 entrance fee

    // The dress rules 1-3 are not hard constraints: breaking one costs the fee.
    // Each rule is a Boolean that is true when the rule holds.

    // rule 1: if he wears a green tie he has to wear a green shirt
    BoolVar rule1 = expr(*this, (t == 0) || (r == 1));

    // rule 2: green socks and a green shirt only if he wears a green tie or a green hat
    BoolVar rule2 = expr(*this, (s == 0) || (r == 0) || (t == 1) || (h == 1));

    // rule 3: a green shirt, a green hat, or no green socks requires a green tie
    BoolVar rule3 = expr(*this, (r == 0 && h == 0 && s == 1) || (t == 1));

    // rule 4: a guest not dressed according to rules 1-3 pays the 11 entrance fee
    BoolVar dressed = expr(*this, rule1 && rule2 && rule3);
    rel(*this, n, IRT_NQ, dressed);

    // cost: tie 10, hat 2, socks 12, fee 11; the owned green shirt costs nothing, otherwise 9
    cost = expr(*this, 10 * t + 2 * h + 12 * s + 11 * n + 9 - 9 * r);
    minimize(cost);

    // decisions first, then the fee, which propagation fixes
    BoolVarArgs choices;
    choices << t << h << r << s << n;
    branch(*this, choices, BOOL_VAR_NONE(), BOOL_VAL_MIN());

    output("t", t);
    output("h", h);
    output("r", r);
    output("s", s);
    output("n", n);
  }

  FancyDress(FancyDress& sp) : dcp::Space(sp) {
    t.update(*this, sp.t);
    h.update(*this, sp.h);
    r.update(*this, sp.r);
    s.update(*this, sp.s);
    n.update(*this, sp.n);
    cost.update(*this, sp.cost);
  }
  Gecode::Space* copy() override { return new FancyDress(*this); }
};

DCP_MODEL(FancyDress)
