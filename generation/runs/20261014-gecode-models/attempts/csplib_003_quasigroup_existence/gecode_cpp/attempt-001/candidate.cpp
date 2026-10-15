#include "dcp.h"

// QG3.m quasigroup existence: find an order m quasigroup, i.e. an m x m table
// in which every symbol 0..m-1 occurs once in every row and once in every
// column, such that (a*b)*(b*a) = a for all a and b. Satisfaction problem.
class QG3Existence : public dcp::Space {
 protected:
  int order;        // m, the order of the quasigroup, from the instance
  IntVarArray cell; // cell[i*m+j] = i*j, the table in row-major order

 public:
  explicit QG3Existence(const json& instance) {
    order = instance.at("m").get<int>();
    const int m = order;
    cell = IntVarArray(*this, m * m, 0, m - 1);

    IntVarArgs flat;
    for (int k = 0; k < m * m; ++k) flat << cell[k];

    // every row holds each symbol once
    for (int i = 0; i < m; ++i) {
      IntVarArgs row;
      for (int j = 0; j < m; ++j) row << cell[i * m + j];
      distinct(*this, row, IPL_DOM);
    }

    // every column holds each symbol once
    for (int j = 0; j < m; ++j) {
      IntVarArgs col;
      for (int i = 0; i < m; ++i) col << cell[i * m + j];
      distinct(*this, col, IPL_DOM);
    }

    // (a*b)*(b*a) = a: with c = a*b and d = b*a, the entry in row c, column d
    // is a. Matrix-form element reads flat[d + m*c] = a.
    for (int a = 0; a < m; ++a) {
      IntVar symbol(*this, a, a);
      for (int b = 0; b < m; ++b) {
        IntVar c = cell[a * m + b];
        IntVar d = cell[b * m + a];
        element(*this, flat, d, m, c, m, symbol, IPL_DOM);
      }
    }

    branch(*this, cell, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    output("quasigroup", Matrix<IntVarArray>(cell, m, m));
  }

  QG3Existence(QG3Existence& s) : dcp::Space(s), order(s.order) {
    cell.update(*this, s.cell);
  }

  Gecode::Space* copy() override { return new QG3Existence(*this); }
};

DCP_MODEL(QG3Existence)
