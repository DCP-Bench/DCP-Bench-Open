#include "dcp.h"

// Broken weights: a measuring weight of m pounds broke into n pieces. Each piece
// weighs a whole number of pounds, and the pieces can weigh every integer from
// 1 to m on a balance scale (a piece can go on the object's pan, on the weights'
// pan, or stay off the scale). Find the weights of the pieces.
class BrokenWeights : public dcp::Space {
 protected:
  IntVarArray w;       // w[i]: weight of piece i, in pounds
  IntVarArray left;    // left[(k-1)*n+i]: piece i is on the object's pan when weighing k
  IntVarArray right;   // right[(k-1)*n+i]: piece i is on the weights' pan when weighing k

 public:
  explicit BrokenWeights(const json& instance) {
    int m = instance.at("m").get<int>();  // total weight in pounds
    int n = instance.at("n").get<int>();  // number of pieces

    w = IntVarArray(*this, n, 1, m);
    left = IntVarArray(*this, m * n, 0, 1);
    right = IntVarArray(*this, m * n, 0, 1);

    // the pieces weigh the whole measure together
    linear(*this, w, IRT_EQ, m);

    // symmetry breaking: pieces sorted by weight, strictly increasing
    // (no valid answer in the data repeats a weight)
    for (int i = 0; i + 1 < n; ++i) rel(*this, w[i], IRT_LE, w[i + 1]);

    // every weight from 1 to m can be weighed: for weighing k, the object
    // is balanced by the pieces on the two pans
    for (int k = 1; k <= m; ++k) {
      // a piece sits on at most one pan
      for (int i = 0; i < n; ++i) {
        IntVarArgs pan;
        pan << left[(k - 1) * n + i] << right[(k - 1) * n + i];
        linear(*this, pan, IRT_LQ, 1);
      }

      // pieces on the object's pan minus pieces on the weights' pan equal k
      IntVarArgs terms;
      IntArgs coeffs;
      for (int i = 0; i < n; ++i) {
        IntVar on_left(*this, 0, m);
        mult(*this, w[i], left[(k - 1) * n + i], on_left);
        terms << on_left;
        coeffs << 1;

        IntVar on_right(*this, 0, m);
        mult(*this, w[i], right[(k - 1) * n + i], on_right);
        terms << on_right;
        coeffs << -1;
      }
      linear(*this, coeffs, terms, IRT_EQ, k);
    }

    // search: the piece weights first, then the pan placements of every weighing
    branch(*this, w, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    branch(*this, left, INT_VAR_NONE(), INT_VAL_MIN());
    branch(*this, right, INT_VAR_NONE(), INT_VAL_MIN());

    output("weights", w);
  }

  BrokenWeights(BrokenWeights& s) : dcp::Space(s) {
    w.update(*this, s.w);
    left.update(*this, s.left);
    right.update(*this, s.right);
  }

  Gecode::Space* copy() override { return new BrokenWeights(*this); }
};

DCP_MODEL(BrokenWeights)
