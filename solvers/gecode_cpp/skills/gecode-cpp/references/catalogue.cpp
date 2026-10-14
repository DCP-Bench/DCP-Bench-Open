// Checks the semantics of Gecode 6.2.0 constraints against brute force.
// Each check posts a constraint on v (ints in [lo, hi]) and b (Booleans), counts the
// solutions with DFS, and compares with a brute-force count of a predicate.
// Build: g++ -std=c++17 catalogue.cpp -lgecodesearch -lgecodeminimodel -lgecodeset
//        -lgecodefloat -lgecodeint -lgecodekernel -lgecodesupport
#include <gecode/int.hh>
#include <gecode/set.hh>
#include <gecode/minimodel.hh>
#include <gecode/search.hh>
#include <algorithm>
#include <functional>
#include <iostream>
#include <vector>
#include <cstdlib>
using namespace Gecode;
using V = std::vector<int>;

struct T : Space {
  IntVarArray v;
  BoolVarArray b;
  T(int n, int lo, int hi, int nb) : v(*this, n, lo, hi), b(*this, nb, 0, 1) {}
  T(T& s) : Space(s) { v.update(*this, s.v); b.update(*this, s.b); }
  Space* copy() override { return new T(*this); }
};

int failures = 0;

void check(const char* name, int n, int lo, int hi, int nb, std::function<void(T&)> post,
           std::function<bool(const V&, const V&)> pred) {
  T* s = new T(n, lo, hi, nb);
  post(*s);
  branch(*s, s->v, INT_VAR_NONE(), INT_VAL_MIN());
  if (nb) branch(*s, s->b, BOOL_VAR_NONE(), BOOL_VAL_MIN());
  long got = 0;
  bool leftover = false;
  {
    DFS<T> e(s);
    while (T* sol = e.next()) {
      ++got;
      if (PropagatorGroup::all.size(*sol) > 0) leftover = true;
      delete sol;
    }
  }
  delete s;
  long want = 0;
  V x(n, lo), y(nb, 0);
  while (true) {
    if (pred(x, y)) ++want;
    int i = 0;
    for (; i < n; ++i) { if (x[i] < hi) { ++x[i]; break; } x[i] = lo; }
    if (i < n) continue;
    int j = 0;
    for (; j < nb; ++j) { if (y[j] < 1) { ++y[j]; break; } y[j] = 0; }
    if (j < nb) continue;
    break;
  }
  bool ok = got == want;
  if (!ok) ++failures;
  std::cout << (ok ? "ok   " : "FAIL ") << name << " gecode=" << got << " brute=" << want
            << (leftover ? " LEFTOVER-PROPAGATORS" : "") << "\n";
}

IntVarArgs sl(const IntVarArray& a, int from, int len) {
  IntVarArgs r;
  for (int i = 0; i < len; ++i) r << a[from + i];
  return r;
}
bool alldiff(const V& x, int from, int len) {
  for (int i = from; i < from + len; ++i)
    for (int j = i + 1; j < from + len; ++j)
      if (x[i] == x[j]) return false;
  return true;
}

int main() {
  // --- distinct family
  check("distinct", 4, 0, 3, 0, [](T& s) { distinct(s, s.v, IPL_DOM); },
        [](const V& x, const V&) { return alldiff(x, 0, 4); });
  check("distinct offsets x_i+n_i", 4, 0, 3, 0, [](T& s) { distinct(s, IntArgs({0, 1, 2, 3}), s.v); },
        [](const V& x, const V&) {
          for (int i = 0; i < 4; ++i) for (int j = i + 1; j < 4; ++j) if (x[i] + i == x[j] + j) return false;
          return true; });
  check("distinct except c", 3, 0, 2, 0, [](T& s) { distinct(s, s.v, 0); },
        [](const V& x, const V&) {
          for (int i = 0; i < 3; ++i) for (int j = i + 1; j < 3; ++j) if (x[i] == x[j] && x[i] != 0) return false;
          return true; });
  check("distinct optional b", 3, 0, 1, 3, [](T& s) { distinct(s, s.b, s.v); },
        [](const V& x, const V& b) {
          for (int i = 0; i < 3; ++i) for (int j = i + 1; j < 3; ++j) if (b[i] && b[j] && x[i] == x[j]) return false;
          return true; });

  // --- counting
  check("count x==1 exactly 2", 4, 0, 2, 0, [](T& s) { count(s, s.v, 1, IRT_EQ, 2); },
        [](const V& x, const V&) { int c = 0; for (int a : x) c += a == 1; return c == 2; });
  check("count x in set >= 2", 4, 0, 3, 0, [](T& s) { count(s, s.v, IntSet({1, 3}), IRT_GQ, 2); },
        [](const V& x, const V&) { int c = 0; for (int a : x) c += a == 1 || a == 3; return c >= 2; });
  check("count var value y, var count z", 5, 0, 3, 0,  // x = v0..v2, y = v3, z = v4
        [](T& s) { count(s, sl(s.v, 0, 3), s.v[3], IRT_EQ, s.v[4]); },
        [](const V& x, const V&) { int c = 0; for (int i = 0; i < 3; ++i) c += x[i] == x[3]; return c == x[4]; });
  check("gcc count(x, cards, vals)", 6, 0, 3, 0,  // x = v0..v3 over {1,2}, cards c1 = v4, c2 = v5
        [](T& s) { dom(s, sl(s.v, 0, 4), 1, 2); count(s, sl(s.v, 0, 4), sl(s.v, 4, 2), IntArgs({1, 2})); },
        [](const V& x, const V&) {
          int c1 = 0, c2 = 0;
          for (int i = 0; i < 4; ++i) { if (x[i] < 1 || x[i] > 2) return false; c1 += x[i] == 1; c2 += x[i] == 2; }
          return c1 == x[4] && c2 == x[5]; });
  check("gcc count(x, IntSetArgs, vals) bounds", 4, 0, 2, 0,
        [](T& s) { count(s, s.v, IntSetArgs({IntSet(1, 2), IntSet(0, 1), IntSet(0, 4)}), IntArgs({0, 1, 2})); },
        [](const V& x, const V&) {
          int c[3] = {0, 0, 0}; for (int a : x) ++c[a];
          return c[0] >= 1 && c[0] <= 2 && c[1] <= 1; });
  check("nvalues == 2", 4, 0, 2, 0, [](T& s) { nvalues(s, s.v, IRT_EQ, 2); },
        [](const V& x, const V&) { int m = 0; for (int v = 0; v <= 2; ++v) for (int a : x) if (a == v) { ++m; break; } return m == 2; });
  check("sequence q=3 in {1} between 1 and 2", 6, 0, 1, 0, [](T& s) { sequence(s, s.v, IntSet({1}), 3, 1, 2); },
        [](const V& x, const V&) {
          for (int i = 0; i + 3 <= 6; ++i) { int c = x[i] + x[i + 1] + x[i + 2]; if (c < 1 || c > 2) return false; }
          return true; });
  check("linear bool sum == 2", 0, 0, 0, 4, [](T& s) { linear(s, s.b, IRT_EQ, 2); },
        [](const V&, const V& b) { return b[0] + b[1] + b[2] + b[3] == 2; });

  // --- element and tables
  check("element(IntArgs, idx, val)", 2, 0, 9, 0, [](T& s) { element(s, IntArgs({5, 7, 9}), s.v[0], s.v[1]); },
        [](const V& x, const V&) { int a[] = {5, 7, 9}; return x[0] <= 2 && a[x[0]] == x[1]; });
  check("element(IntVarArgs, idx, val)", 5, 0, 3, 0, [](T& s) { element(s, sl(s.v, 0, 3), s.v[3], s.v[4]); },
        [](const V& x, const V&) { return x[3] <= 2 && x[x[3]] == x[4]; });
  check("element matrix a[x + w*y]", 3, 0, 6, 0,  // a is 3 wide (w) x 2 high (h)
        [](T& s) { element(s, IntArgs({1, 2, 3, 4, 5, 6}), s.v[0], 3, s.v[1], 2, s.v[2]); },
        [](const V& x, const V&) { return x[0] < 3 && x[1] < 2 && x[2] == 1 + x[0] + 3 * x[1]; });
  check("MiniModel element(IntArgs, expr)", 2, 0, 9, 0,
        [](T& s) { rel(s, element(IntArgs({4, 8, 6}), s.v[0]) == s.v[1]); },
        [](const V& x, const V&) { int a[] = {4, 8, 6}; return x[0] <= 2 && a[x[0]] == x[1]; });
  check("extensional TupleSet", 3, 0, 2, 0,
        [](T& s) {
          TupleSet t(3);
          t.add(IntArgs({0, 1, 2})).add(IntArgs({1, 1, 1})).add(IntArgs({2, 0, 0}));
          t.finalize();
          extensional(s, s.v, t); },
        [](const V& x, const V&) {
          return (x == V{0, 1, 2}) || (x == V{1, 1, 1}) || (x == V{2, 0, 0}); });
  check("extensional TupleSet negative", 2, 0, 2, 0,
        [](T& s) { TupleSet t(2); t.add(IntArgs({0, 0})).add(IntArgs({1, 1})); t.finalize(); extensional(s, s.v, t, false); },
        [](const V& x, const V&) { return !(x == V{0, 0} || x == V{1, 1}); });
  check("extensional REG nonogram clue 2 1 on 6 cells", 6, 0, 1, 0,
        [](T& s) {
          REG r0(0), r1(1);
          REG clue = *r0 + r1(2, 2) + +r0 + r1(1, 1) + *r0;
          extensional(s, s.v, DFA(clue)); },
        [](const V& x, const V&) {
          std::vector<int> blocks; int run = 0;
          for (int i = 0; i < 6; ++i) { if (x[i]) ++run; else if (run) { blocks.push_back(run); run = 0; } }
          if (run) blocks.push_back(run);
          return blocks == std::vector<int>{2, 1}; });

  check("extensional hand-built DFA: no two 1s in a row", 5, 0, 1, 0,
        [](T& s) {
          DFA::Transition t[] = {{0, 0, 0}, {0, 1, 1}, {1, 0, 0}, {-1, 0, 0}};
          int f[] = {0, 1, -1};
          extensional(s, s.v, DFA(0, t, f)); },
        [](const V& x, const V&) { for (int i = 0; i + 1 < 5; ++i) if (x[i] && x[i + 1]) return false; return true; });

  // --- graphs: circuit / path (successor arrays)
  check("circuit", 4, 0, 3, 0, [](T& s) { circuit(s, s.v); },
        [](const V& x, const V&) {
          int c = 0, seen = 0; do { c = x[c]; ++seen; } while (c != 0 && seen <= 4);
          if (seen != 4) return false; V y(x); std::sort(y.begin(), y.end()); return y == V{0, 1, 2, 3}; });
  check("circuit offset 1", 4, 1, 4, 0, [](T& s) { circuit(s, 1, s.v); },
        [](const V& x, const V&) {
          int c = 1, seen = 0; do { c = x[c - 1]; ++seen; } while (c != 1 && seen <= 4);
          V y(x); std::sort(y.begin(), y.end()); return seen == 4 && y == V{1, 2, 3, 4}; });
  check("circuit with cost z = sum c[i][x_i]", 4, 0, 30, 0,  // x = v0..v2 (n = 3), z = v3
        [](T& s) {
          dom(s, sl(s.v, 0, 3), 0, 2);
          IntArgs c({0, 1, 2, 3, 0, 4, 5, 6, 0});  // row-major n x n
          circuit(s, c, sl(s.v, 0, 3), s.v[3]); },
        [](const V& x, const V&) {
          for (int i = 0; i < 3; ++i) if (x[i] > 2) return false;
          int c[] = {0, 1, 2, 3, 0, 4, 5, 6, 0};
          bool cyc = (x[0] == 1 && x[1] == 2 && x[2] == 0) || (x[0] == 2 && x[2] == 1 && x[1] == 0);
          return cyc && x[3] == c[0 * 3 + x[0]] + c[1 * 3 + x[1]] + c[2 * 3 + x[2]]; });
  check("path(x, s, e): x[e] = n", 5, 0, 3, 0,  // nodes 0..2: x = v0..v2, start v3, end v4
        [](T& s) { path(s, sl(s.v, 0, 3), s.v[3], s.v[4]); },
        [](const V& x, const V&) {
          int st = x[3], en = x[4];
          if (st > 2 || en > 2 || x[en] != 3) return false;
          int c = st, seen = 1; while (c != en && seen <= 3) { if (x[c] > 2) return false; c = x[c]; ++seen; }
          return seen == 3; });

  // --- scheduling and packing
  check("unary s, p={2,2}", 2, 0, 4, 0, [](T& s) { unary(s, s.v, IntArgs({2, 2})); },
        [](const V& x, const V&) { return x[0] + 2 <= x[1] || x[1] + 2 <= x[0]; });
  check("unary optional", 2, 0, 3, 2, [](T& s) { unary(s, s.v, IntArgs({2, 2}), s.b); },
        [](const V& x, const V& b) { return !(b[0] && b[1]) || x[0] + 2 <= x[1] || x[1] + 2 <= x[0]; });
  check("cumulative c=2", 3, 0, 3, 0, [](T& s) { cumulative(s, 2, s.v, IntArgs({2, 2, 2}), IntArgs({1, 1, 1})); },
        [](const V& x, const V&) {
          for (int t = 0; t < 6; ++t) { int u = 0; for (int i = 0; i < 3; ++i) u += x[i] <= t && t < x[i] + 2; if (u > 2) return false; }
          return true; });
  check("nooverlap fixed sizes", 4, 0, 2, 0,  // rects 2x1 and 1x2: x0 = v0, x1 = v1, y0 = v2, y1 = v3
        [](T& s) { nooverlap(s, sl(s.v, 0, 2), IntArgs({2, 1}), sl(s.v, 2, 2), IntArgs({1, 2})); },
        [](const V& x, const V&) {
          int w[] = {2, 1}, h[] = {1, 2};
          return x[0] + w[0] <= x[1] || x[1] + w[1] <= x[0] || x[2] + h[0] <= x[3] || x[3] + h[1] <= x[2]; });
  check("binpacking l=loads b=bins s=sizes", 5, 0, 5, 0,  // loads v0..v1, bins v2..v4
        [](T& s) { dom(s, sl(s.v, 2, 3), 0, 1); binpacking(s, sl(s.v, 0, 2), sl(s.v, 2, 3), IntArgs({2, 2, 1})); },
        [](const V& x, const V&) {
          int sz[] = {2, 2, 1}, l[2] = {0, 0};
          for (int i = 0; i < 3; ++i) { if (x[2 + i] > 1) return false; l[x[2 + i]] += sz[i]; }
          return l[0] == x[0] && l[1] == x[1]; });

  // --- ordering, channelling, symmetry
  check("sorted(x, y)", 4, 0, 2, 0, [](T& s) { sorted(s, sl(s.v, 0, 2), sl(s.v, 2, 2)); },
        [](const V& x, const V&) { return std::min(x[0], x[1]) == x[2] && std::max(x[0], x[1]) == x[3]; });
  check("channel(x, y) inverse permutation", 6, 0, 2, 0, [](T& s) { channel(s, sl(s.v, 0, 3), sl(s.v, 3, 3)); },
        [](const V& x, const V&) { for (int i = 0; i < 3; ++i) if (x[3 + x[i]] != i) return false; return alldiff(x, 0, 3); });
  check("channel(bools, int, offset 1)", 1, 0, 4, 3, [](T& s) { channel(s, s.b, s.v[0], 1); },
        [](const V& x, const V& b) { for (int i = 0; i < 3; ++i) if (b[i] != (x[0] == i + 1)) return false; return x[0] >= 1 && x[0] <= 3; });
  check("channel(BoolVar, IntVar)", 1, 0, 1, 1, [](T& s) { channel(s, s.b[0], s.v[0]); },
        [](const V& x, const V& b) { return x[0] == b[0]; });
  check("precede(x, 0, 1)", 3, 0, 2, 0, [](T& s) { precede(s, s.v, 0, 1); },
        [](const V& x, const V&) { for (int i = 0; i < 3; ++i) { if (x[i] == 0) return true; if (x[i] == 1) return false; } return true; });
  check("precede(x, {0,1,2})", 3, 0, 2, 0, [](T& s) { precede(s, s.v, IntArgs({0, 1, 2})); },
        [](const V& x, const V&) {
          int top = -1; for (int a : x) { if (a > top + 1) return false; top = std::max(top, a); } return true; });
  check("lex x <= y", 4, 0, 1, 0, [](T& s) { rel(s, sl(s.v, 0, 2), IRT_LQ, sl(s.v, 2, 2)); },
        [](const V& x, const V&) { return V{x[0], x[1]} <= V{x[2], x[3]}; });
  check("chain rel(x, IRT_LE)", 3, 0, 3, 0, [](T& s) { rel(s, s.v, IRT_LE); },
        [](const V& x, const V&) { return x[0] < x[1] && x[1] < x[2]; });
  check("member(x, y)", 3, 0, 2, 0, [](T& s) { member(s, sl(s.v, 0, 2), s.v[2]); },
        [](const V& x, const V&) { return x[2] == x[0] || x[2] == x[1]; });

  // --- arithmetic
  check("max(x, y)", 3, 0, 2, 0, [](T& s) { max(s, sl(s.v, 0, 2), s.v[2]); },
        [](const V& x, const V&) { return x[2] == std::max(x[0], x[1]); });
  check("argmax first index", 4, 0, 2, 0, [](T& s) { argmax(s, sl(s.v, 0, 3), s.v[3]); },
        [](const V& x, const V&) { int a = 0; for (int i = 1; i < 3; ++i) if (x[i] > x[a]) a = i; return x[3] == a; });
  check("abs/mult/div/mod via MiniModel", 4, -3, 3, 0,
        [](T& s) { rel(s, abs(s.v[0]) == s.v[1]); rel(s, s.v[2] * s.v[3] == s.v[1]); },
        [](const V& x, const V&) { return std::abs(x[0]) == x[1] && x[2] * x[3] == x[1]; });
  check("divmod", 4, 0, 7, 0, [](T& s) { rel(s, s.v[1] == 3); divmod(s, s.v[0], s.v[1], s.v[2], s.v[3]); },
        [](const V& x, const V&) { return x[1] == 3 && x[2] == x[0] / 3 && x[3] == x[0] % 3; });
  check("linear coefficients", 3, 0, 4, 0, [](T& s) { linear(s, IntArgs({1, 2, -1}), s.v, IRT_EQ, 3); },
        [](const V& x, const V&) { return x[0] + 2 * x[1] - x[2] == 3; });

  // --- reification and Boolean logic
  check("expr reified b <-> x0<x1", 2, 0, 2, 1,
        [](T& s) { rel(s, s.b[0] == (s.v[0] < s.v[1])); },
        [](const V& x, const V& b) { return b[0] == (x[0] < x[1]); });
  check("Reify imp: b -> x0==x1", 2, 0, 2, 1, [](T& s) { rel(s, s.v[0], IRT_EQ, s.v[1], imp(s.b[0])); },
        [](const V& x, const V& b) { return !b[0] || x[0] == x[1]; });
  check("BoolExpr implication >>", 2, 0, 2, 0, [](T& s) { rel(s, (s.v[0] == 1) >> (s.v[1] != 1)); },
        [](const V& x, const V&) { return x[0] != 1 || x[1] != 1; });
  check("ite(b, x, y, z)", 3, 0, 2, 1, [](T& s) { ite(s, s.b[0], s.v[0], s.v[1], s.v[2]); },
        [](const V& x, const V& b) { return x[2] == (b[0] ? x[0] : x[1]); });
  check("clause or(pos, neg)", 0, 0, 0, 3,
        [](T& s) { clause(s, BOT_OR, BoolVarArgs({s.b[0], s.b[1]}), BoolVarArgs({s.b[2]}), 1); },
        [](const V&, const V& b) { return b[0] || b[1] || !b[2]; });
  check("linear reified count of x==1", 4, 0, 2, 0,
        [](T& s) { rel(s, expr(s, s.v[0] == 1) + expr(s, s.v[1] == 1) + expr(s, s.v[2] == 1) == s.v[3]); },
        [](const V& x, const V&) { return (x[0] == 1) + (x[1] == 1) + (x[2] == 1) == x[3]; });

  // --- sets, channelled to Booleans for output
  check("set var: |s| = 2 channelled to bools", 0, 0, 0, 4,
        [](T& s) { SetVar set(s, IntSet::empty, 0, 3); channel(s, s.b, set); cardinality(s, set, 2, 2); },
        [](const V&, const V& b) { return b[0] + b[1] + b[2] + b[3] == 2; });

  // --- LDSB: values interchangeable; only checks that it runs and prunes
  {
    T* s = new T(3, 0, 2, 0);
    distinct(*s, s->v);
    Symmetries syms;
    syms << ValueSymmetry(IntArgs({0, 1, 2}));
    branch(*s, s->v, INT_VAR_NONE(), INT_VAL_MIN(), syms);
    DFS<T> e(s);
    int n = 0;
    while (T* sol = e.next()) { ++n; delete sol; }
    delete s;
    std::cout << (n == 1 ? "ok   " : "FAIL ") << "LDSB value symmetry: 1 of 6 permutations, got " << n << "\n";
    if (n != 1) ++failures;
  }

  std::cout << (failures ? "FAILURES " : "ALL OK ") << failures << "\n";
  return failures ? 1 : 0;
}
