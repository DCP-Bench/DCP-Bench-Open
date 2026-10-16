#include "dcp.h"

// Costas array problem: place n marks on an n x n grid, one per row and column,
// so that the n(n-1)/2 vectors between pairs of marks are all different.
// costas[i] is the column of the mark in row i (1-based values 1..n).
class Costas : public dcp::Space {
 protected:
  int n;
  IntVarArray costas;                 // costas[i]: column of the mark in row i+1
  std::vector<IntVarArray> triangle;  // triangle[l-1][i]: X_{i+1} - X_{i+1+l}, l = 1..n-1

 public:
  explicit Costas(const json& instance) {
    n = instance.at("n").get<int>();

    // one mark per row and one per column: the marks form a permutation
    costas = IntVarArray(*this, n, 1, n);
    distinct(*this, costas, IPL_DOM);

    // difference triangle: for each length l, the differences X_i - X_{i+l}
    triangle.resize(n - 1);
    for (int l = 1; l <= n - 1; ++l) {
      triangle[l - 1] = IntVarArray(*this, n - l, -(n - 1), n - 1);
      for (int i = 0; i < n - l; ++i) {
        // the difference of two marks is the difference of their columns
        rel(*this, triangle[l - 1][i] == costas[i] - costas[i + l]);
        // two distinct columns never give a zero difference
        rel(*this, triangle[l - 1][i] != 0);
      }
      // each line of the difference triangle contains no value twice
      distinct(*this, triangle[l - 1], IPL_DOM);
    }

    // branch on the marks first: they fix the whole difference triangle
    branch(*this, costas, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    for (int l = 0; l < n - 1; ++l)
      branch(*this, triangle[l], INT_VAR_SIZE_MIN(), INT_VAL_MIN());

    output("costas", costas);
  }

  Costas(Costas& s) : dcp::Space(s), n(s.n) {
    costas.update(*this, s.costas);
    triangle.resize(s.triangle.size());
    for (std::size_t l = 0; l < s.triangle.size(); ++l) triangle[l].update(*this, s.triangle[l]);
  }
  Gecode::Space* copy() override { return new Costas(*this); }
};

DCP_MODEL(Costas)
