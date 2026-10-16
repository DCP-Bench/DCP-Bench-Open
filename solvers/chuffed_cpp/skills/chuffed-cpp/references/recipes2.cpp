// Cheat-sheet check 2: circuit, table, cumulative, disjunctive, regular and Boolean constraints.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  // succ[i] is the node visited after node i; the four nodes form one tour
  vec<IntVar*> succ;
  createVars(succ, 4, 0, 3);
  circuit(succ);

  // the pair (a, b) must be one of the allowed pairs
  vec<IntVar*> ab;
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
  vec<IntVar*> s;
  createVars(s, 3, 0, 5);
  vec<int> d, res;
  d.push(2); d.push(3); d.push(2);
  res.push(1); res.push(1); res.push(1);
  cumulative(s, d, res, 2);
  vec<IntVar*> s01; s01.push(s[0]); s01.push(s[1]);
  vec<int> d01; d01.push(2); d01.push(3);
  disjunctive(s01, d01);

  // a sequence of four symbols from {1, 2} has no two consecutive 2s (DFA: state 1 = last symbol 1, state 2 = last symbol 2, 0 = reject)
  vec<IntVar*> seq;
  createVars(seq, 4, 1, 2);
  vec<vec<int>> dfa;
  dfa.push(); dfa.last().push(1); dfa.last().push(2);   // state 1: sym1->1, sym2->2
  dfa.push(); dfa.last().push(1); dfa.last().push(0);   // state 2: sym1->1, sym2->reject
  vec<int> accept; accept.push(1); accept.push(2);
  regular(seq, 2, 2, dfa, 1, accept);

  // p or q or not r holds, and at least two of p, q, r are true
  vec<BoolView> bs;
  createVars(bs, 3);
  vec<BoolView> pos, neg;
  pos.push(bs[0]); pos.push(bs[1]); neg.push(bs[2]);
  bool_clause(pos, neg);
  IntVar* two = getConstant(2);
  bool_linear(bs, IRT_GE, two);
  json bo = json::array();
  for (int i = 0; i < 3; ++i) {
    IntVar* bi = newIntVar(0, 1);
    bool2int(bs[i], bi);
    bo.push_back(dcp::out(bi));
  }

  vec<IntVar*> all;
  for (int i = 0; i < 4; ++i) all.push(succ[i]);
  all.push(ab[0]); all.push(ab[1]);
  for (int i = 0; i < 3; ++i) all.push(s[i]);
  for (int i = 0; i < 4; ++i) all.push(seq[i]);
  branch(all, VAR_INORDER, VAL_MIN);

  auto arr = [](vec<IntVar*>& v) { json a = json::array(); for (int i = 0; i < v.size(); ++i) a.push_back(dcp::out(v[i])); return a; };
  outputs = {{"succ", arr(succ)}, {"ab", arr(ab)}, {"s", arr(s)}, {"seq", arr(seq)}, {"bs", bo}};
}
