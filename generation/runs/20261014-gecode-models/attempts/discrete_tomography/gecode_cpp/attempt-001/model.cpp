#include "dcp.h"

// Discrete tomography: fill a matrix of zeroes and ones so that every row and
// every column contains the number of ones given by its X-ray count.
class DiscreteTomography : public dcp::Space {
 protected:
  IntVarArray x;  // x[i * cols + j] is cell (i, j) of the matrix: 0 or 1
  int rows;
  int cols;

 public:
  explicit DiscreteTomography(const json& instance) {
    std::vector<int> row_sums = instance.at("row_sums").get<std::vector<int>>();
    std::vector<int> col_sums = instance.at("col_sums").get<std::vector<int>>();
    rows = static_cast<int>(row_sums.size());
    cols = static_cast<int>(col_sums.size());
    x = IntVarArray(*this, rows * cols, 0, 1);

    // each row contains as many ones as its horizontal X-ray count
    for (int i = 0; i < rows; ++i) {
      IntVarArgs row;
      for (int j = 0; j < cols; ++j) row << x[i * cols + j];
      count(*this, row, 1, IRT_EQ, row_sums[i]);
    }

    // each column contains as many ones as its vertical X-ray count
    for (int j = 0; j < cols; ++j) {
      IntVarArgs col;
      for (int i = 0; i < rows; ++i) col << x[i * cols + j];
      count(*this, col, 1, IRT_EQ, col_sums[j]);
    }

    // search: the matrix cells are the only decisions. Cells are 0/1, so the
    // branching is on the cells themselves with the 0 value tried first.
    branch(*this, x, INT_VAR_AFC_SIZE_MAX(0.99), INT_VAL_MIN());
    restarts(100);

    // print the matrix one row per list
    std::vector<IntVarArgs> matrix(rows);
    for (int i = 0; i < rows; ++i)
      for (int j = 0; j < cols; ++j) matrix[i] << x[i * cols + j];
    output("matrix", matrix);
  }

  DiscreteTomography(DiscreteTomography& s) : dcp::Space(s), rows(s.rows), cols(s.cols) {
    x.update(*this, s.x);
  }
  Gecode::Space* copy() override { return new DiscreteTomography(*this); }
};

DCP_MODEL(DiscreteTomography)
