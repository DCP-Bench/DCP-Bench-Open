// Fancy dress party: Mr Greenguest chooses which items to wear so that he follows the dress code
// (or pays the 11 dollar fee) at the least cost. He owns a green shirt already, and can buy a
// green tie for 10, a green hat for 2 and green socks for 12. Choices are 0/1 for tie (t),
// hat (h), shirt (r), socks (s) and entrance fee (n).
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  // the five choices as Booleans: t tie, h hat, r shirt, s socks, n pays the entrance fee
  vec<BoolView> choice;
  createVars(choice, 5);
  BoolView t = choice[0];
  BoolView h = choice[1];
  BoolView r = choice[2];
  BoolView s = choice[3];
  BoolView n = choice[4];

  // rule 1: a green tie requires a green shirt (t -> r)
  {
    vec<BoolView> pos, neg;
    pos.push(r);
    neg.push(t);
    bool_clause(pos, neg);
  }

  // rule 2: green socks and a green shirt only if a green tie or a green hat (s and r -> t or h)
  {
    vec<BoolView> pos, neg;
    pos.push(t);
    pos.push(h);
    neg.push(s);
    neg.push(r);
    bool_clause(pos, neg);
  }

  // rule 3: a green shirt, or a green hat, or no green socks requires a green tie
  // ((r or h or not s) -> t) is the three clauses (t or not r), (t or not h), (t or s)
  {
    vec<BoolView> pos, neg;
    pos.push(t);
    neg.push(r);
    bool_clause(pos, neg);
  }
  {
    vec<BoolView> pos, neg;
    pos.push(t);
    neg.push(h);
    bool_clause(pos, neg);
  }
  {
    vec<BoolView> pos, neg;
    pos.push(t);
    pos.push(s);
    bool_clause(pos, neg);
  }

  // rule 4: a guest who breaks rules 1 to 3 pays the fee, so n is true whenever a rule is broken.
  // Each clause of rules 1 to 3 is kept unless n is true: (n or clause) for every clause.
  {
    vec<BoolView> pos, neg;
    pos.push(n);
    pos.push(r);
    neg.push(t);
    bool_clause(pos, neg);
  }
  {
    vec<BoolView> pos, neg;
    pos.push(n);
    pos.push(t);
    pos.push(h);
    neg.push(s);
    neg.push(r);
    bool_clause(pos, neg);
  }
  {
    vec<BoolView> pos, neg;
    pos.push(n);
    pos.push(t);
    neg.push(r);
    bool_clause(pos, neg);
  }
  {
    vec<BoolView> pos, neg;
    pos.push(n);
    pos.push(t);
    neg.push(h);
    bool_clause(pos, neg);
  }
  {
    vec<BoolView> pos, neg;
    pos.push(n);
    pos.push(t);
    pos.push(s);
    bool_clause(pos, neg);
  }

  // the 0/1 integer copies of the choices, for the output and the cost
  IntVar* ti = newIntVar(0, 1);
  bool2int(t, ti);
  IntVar* hi = newIntVar(0, 1);
  bool2int(h, hi);
  IntVar* ri = newIntVar(0, 1);
  bool2int(r, ri);
  IntVar* si = newIntVar(0, 1);
  bool2int(s, si);
  IntVar* ni = newIntVar(0, 1);
  bool2int(n, ni);

  // the cost: tie 10, hat 2, socks 12 and fee 11; the green shirt is already owned, so it costs nothing
  vec<int> prices;
  prices.push(10);
  prices.push(2);
  prices.push(12);
  prices.push(11);
  vec<IntVar*> bought;
  bought.push(ti);
  bought.push(hi);
  bought.push(si);
  bought.push(ni);
  IntVar* cost = newIntVar(0, 35);
  int_linear(prices, bought, IRT_EQ, cost);

  // the choices are the decision variables
  vec<IntVar*> search;
  search.push(ti);
  search.push(hi);
  search.push(ri);
  search.push(si);
  search.push(ni);
  branch(search, VAR_INORDER, VAL_MIN);

  // minimise the cost
  optimize(cost, OPT_MIN);

  outputs = {{"h", dcp::out(hi)}, {"n", dcp::out(ni)}, {"r", dcp::out(ri)},
             {"s", dcp::out(si)}, {"t", dcp::out(ti)}};
}
