// A tour of Chuffed's global constraints on tiny data: circuit, table, cumulative,
// disjunctive, regular, and Boolean clauses and counts.
#include <chuffed/branching/branching.h>
#include <chuffed/core/engine.h>
#include <chuffed/core/options.h>
#include <chuffed/globals/globals.h>
#include <chuffed/primitives/primitives.h>
#include <chuffed/support/vec.h>
#include <chuffed/vars/int-var.h>
#include <chuffed/vars/modelling.h>

#include <cstdlib>
#include <iostream>
#include <ostream>

class Globals : public Problem {
 public:
  vec<IntVar*> succ, ab, s, seq, bint;
  vec<BoolView> bs;

  Globals() {
    // succ[i] is the node visited after node i; the four nodes form one tour
    createVars(succ, 4, 0, 3);
    circuit(succ);

    // the pair (a, b) must be one of the allowed pairs
    createVars(ab, 2, 0, 3);
    vec<vec<int>> tuples;
    int allowed[4][2] = {{0, 1}, {1, 2}, {2, 2}, {3, 0}};
    for (auto& t : allowed) {
      tuples.push();
      tuples.last().push(t[0]);
      tuples.last().push(t[1]);
    }
    table(ab, tuples);

    // three tasks of length 2, 3, 2 need one worker each and at most 2 workers are available;
    // tasks 0 and 1 use the same machine and cannot overlap
    createVars(s, 3, 0, 5);
    vec<int> d, res;
    d.push(2); d.push(3); d.push(2);
    res.push(1); res.push(1); res.push(1);
    cumulative(s, d, res, 2);
    vec<IntVar*> s01; s01.push(s[0]); s01.push(s[1]);
    vec<int> d01; d01.push(2); d01.push(3);
    disjunctive(s01, d01);

    // a sequence of four symbols from {1, 2} has no two consecutive 2s (DFA: state 1 = last symbol 1, state 2 = last symbol 2, 0 = reject)
    createVars(seq, 4, 1, 2);
    vec<vec<int>> dfa;
    dfa.push(); dfa.last().push(1); dfa.last().push(2);   // state 1: sym1->1, sym2->2
    dfa.push(); dfa.last().push(1); dfa.last().push(0);   // state 2: sym1->1, sym2->reject
    vec<int> accept; accept.push(1); accept.push(2);
    regular(seq, 2, 2, dfa, 1, accept);

    // p or q or not r holds, and at least two of p, q, r are true
    createVars(bs, 3);
    vec<BoolView> pos, neg;
    pos.push(bs[0]); pos.push(bs[1]); neg.push(bs[2]);
    bool_clause(pos, neg);
    IntVar* two = getConstant(2);
    bool_linear(bs, IRT_GE, two);

    // branch cannot take BoolViews: link each to a 0..1 IntVar and branch on that.
    // A Boolean no branch reaches stays unfixed, and getVal() then reads 0.
    for (int i = 0; i < 3; ++i) {
      IntVar* bi = newIntVar(0, 1);
      bool2int(bs[i], bi);
      bint.push(bi);
    }

    vec<IntVar*> all;
    for (int i = 0; i < 4; ++i) all.push(succ[i]);
    all.push(ab[0]); all.push(ab[1]);
    for (int i = 0; i < 3; ++i) all.push(s[i]);
    for (int i = 0; i < 4; ++i) all.push(seq[i]);
    for (int i = 0; i < 3; ++i) all.push(bint[i]);
    branch(all, VAR_INORDER, VAL_MIN);
  }

  void print(std::ostream& os) override {
    auto row = [&](const char* name, vec<IntVar*>& v) {
      os << name << " =";
      for (int i = 0; i < v.size(); ++i) os << ' ' << v[i]->getVal();
      os << "; ";
    };
    row("succ", succ);
    row("ab", ab);
    row("s", s);
    row("seq", seq);
    os << "bs =";
    for (int i = 0; i < bs.size(); ++i) os << ' ' << bs[i].getVal();  // BoolView: b.getVal()
    os << "\n";
  }
};

int main() {
  so.print_sol = true;
  engine.solve(new Globals());
  std::cout << "solutions " << engine.solutions << std::endl;
  return 0;
}
