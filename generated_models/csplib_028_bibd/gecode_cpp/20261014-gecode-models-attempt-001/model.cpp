#include "dcp.h"

// Balanced incomplete block design (BIBD) with parameters (v, b, r, k, lambda).
// Decide a v-by-b 0/1 incidence matrix: every object (row) occurs in exactly r
// blocks, every block (column) holds exactly k objects, and every two distinct
// objects occur together in exactly lambda blocks.
class BIBD : public dcp::Space {
 protected:
  int v;  // number of objects (rows)
  int b;  // number of blocks (columns)
  BoolVarArray x;  // x[i * b + c] = 1 if object i occurs in block c

 public:
  explicit BIBD(const json& instance)
      : v(instance.at("v").get<int>()), b(instance.at("b").get<int>()) {
    int r = instance.at("r").get<int>();
    int k = instance.at("k").get<int>();
    int lambda = instance.at("l").get<int>();
    x = BoolVarArray(*this, v * b, 0, 1);

    // each object occurs in exactly r blocks
    for (int i = 0; i < v; ++i) {
      BoolVarArgs row;
      for (int c = 0; c < b; ++c) row << x[i * b + c];
      linear(*this, row, IRT_EQ, r);
    }

    // each block contains exactly k objects
    for (int c = 0; c < b; ++c) {
      BoolVarArgs column;
      for (int i = 0; i < v; ++i) column << x[i * b + c];
      linear(*this, column, IRT_EQ, k);
    }

    // every two distinct objects occur together in exactly lambda blocks:
    // the scalar product of their rows is lambda
    for (int i = 0; i < v; ++i) {
      for (int j = i + 1; j < v; ++j) {
        BoolVarArgs both;
        for (int c = 0; c < b; ++c) both << expr(*this, x[i * b + c] && x[j * b + c]);
        linear(*this, both, IRT_EQ, lambda);
      }
    }

    // symmetry breaking: objects are interchangeable, so the rows are in
    // lexicographic order
    for (int i = 0; i + 1 < v; ++i) {
      BoolVarArgs row_a, row_b;
      for (int c = 0; c < b; ++c) {
        row_a << x[i * b + c];
        row_b << x[(i + 1) * b + c];
      }
      rel(*this, row_a, IRT_LQ, row_b);
    }

    // blocks are interchangeable too, so the columns are in lexicographic order
    // (double lex is sound for a matrix whose rows and columns are both symmetric)
    for (int c = 0; c + 1 < b; ++c) {
      BoolVarArgs col_a, col_b;
      for (int i = 0; i < v; ++i) {
        col_a << x[i * b + c];
        col_b << x[i * b + c + 1];
      }
      rel(*this, col_a, IRT_LQ, col_b);
    }

    // satisfaction search with conflict-driven variable choice and restarts
    branch(*this, x, BOOL_VAR_AFC_MAX(0.99), BOOL_VAL_MIN());
    restarts(100);

    std::vector<BoolVarArgs> matrix(v);
    for (int i = 0; i < v; ++i)
      for (int c = 0; c < b; ++c) matrix[i] << x[i * b + c];
    output("matrix", matrix);
  }

  BIBD(BIBD& s) : dcp::Space(s), v(s.v), b(s.b) { x.update(*this, s.x); }

  Gecode::Space* copy() override { return new BIBD(*this); }
};

DCP_MODEL(BIBD)
