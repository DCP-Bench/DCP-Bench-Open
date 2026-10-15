#include "dcp.h"

// Bowls and oranges: m oranges go into n bowls placed in a line at 1 m intervals
// (bowls numbered 1..n). At most one orange per bowl, and no three oranges A, B, C
// with dist(A, B) = dist(B, C). Output the occupied bowls in ascending order.
class BowlsAndOranges : public dcp::Space {
 protected:
  int n;           // number of bowls, from the instance
  IntVarArray x;   // x[i]: bowl of the i-th orange, in ascending order
  IntVarArray o;   // o[k]: 1 when bowl k+1 holds an orange, else 0

 public:
  explicit BowlsAndOranges(const json& instance) {
    n = instance.at("n").get<int>();
    int m = instance.at("m").get<int>();
    x = IntVarArray(*this, m, 1, n);
    o = IntVarArray(*this, n, 0, 1);

    // no more than one orange in each bowl: the bowls are strictly increasing,
    // so no two oranges share one (this also gives the ascending output)
    for (int i = 0; i + 1 < m; ++i) rel(*this, x[i], IRT_LE, x[i + 1]);

    // o[k] is 1 exactly when bowl k+1 holds an orange (count of oranges in that bowl)
    for (int k = 1; k <= n; ++k) count(*this, x, k, IRT_EQ, o[k - 1]);

    // no three oranges A, B, C with dist(A, B) = dist(B, C): for every middle bowl b
    // and gap d, the bowls b-d, b, b+d are not all occupied
    for (int b = 1; b <= n; ++b)
      for (int d = 1; b - d >= 1 && b + d <= n; ++d) {
        IntVarArgs progression;
        progression << o[b - d - 1] << o[b - 1] << o[b + d - 1];
        linear(*this, progression, IRT_LQ, 2);
      }

    // search the oranges' bowls first (first fail, Luby restarts), then the occupancy flags
    branch(*this, x, INT_VAR_AFC_SIZE_MAX(0.99), INT_VAL_MIN());
    branch(*this, o, INT_VAR_NONE(), INT_VAL_MIN());
    restarts(100);

    output("x", x);
  }

  BowlsAndOranges(BowlsAndOranges& s) : dcp::Space(s), n(s.n) {
    x.update(*this, s.x);
    o.update(*this, s.o);
  }
  Gecode::Space* copy() override { return new BowlsAndOranges(*this); }
};

DCP_MODEL(BowlsAndOranges)
