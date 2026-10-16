#include "dcp.h"

// Flip rows and columns of a matrix of signed numbers so that every row and every
// column sums to a non-negative number, then minimise the overall sum of the matrix.
class FlipRowsCols : public dcp::Space {
 protected:
  int rows, cols;
  BoolVarArray rowFlip;   // rowFlip[i] = 1 if row i has its sign flipped
  BoolVarArray colFlip;   // colFlip[j] = 1 if column j has its sign flipped
  BoolVarArray cellFlip;  // cellFlip[i*cols+j] = 1 if entry (i,j) changes sign: rowFlip[i] xor colFlip[j]
  IntVarArray rowSign;    // rowSign[i] in {-1,1}: the sign applied to row i
  IntVarArray colSign;    // colSign[j] in {-1,1}: the sign applied to column j
  IntVar total;           // overall sum of the matrix after the flips

 public:
  explicit FlipRowsCols(const json& instance) {
    std::vector<std::vector<int>> a = instance.at("input_matrix");
    rows = static_cast<int>(a.size());
    cols = static_cast<int>(a[0].size());

    rowFlip = BoolVarArray(*this, rows, 0, 1);
    colFlip = BoolVarArray(*this, cols, 0, 1);
    cellFlip = BoolVarArray(*this, rows * cols, 0, 1);
    rowSign = IntVarArray(*this, rows, -1, 1);
    colSign = IntVarArray(*this, cols, -1, 1);

    // the sign of a row is -1 when the row is flipped, +1 otherwise
    for (int i = 0; i < rows; ++i) rel(*this, rowSign[i] == 1 - 2 * rowFlip[i]);
    // the sign of a column is -1 when the column is flipped, +1 otherwise
    for (int j = 0; j < cols; ++j) rel(*this, colSign[j] == 1 - 2 * colFlip[j]);

    // an entry changes sign exactly when its row or its column is flipped, but not both
    for (int i = 0; i < rows; ++i)
      for (int j = 0; j < cols; ++j)
        rel(*this, rowFlip[i], BOT_XOR, colFlip[j], cellFlip[i * cols + j]);

    // flipping every row and every column together leaves all entries unchanged,
    // so the first row is kept unflipped (symmetry breaking)
    rel(*this, rowFlip[0], IRT_EQ, 0);

    // every row sums to a non-negative number: sum_j a[i][j] * (1 - 2 cellFlip) >= 0
    for (int i = 0; i < rows; ++i) {
      int rowTotal = 0;
      BoolVarArgs cells;
      IntArgs coef(cols);
      for (int j = 0; j < cols; ++j) {
        rowTotal += a[i][j];
        cells << cellFlip[i * cols + j];
        coef[j] = 2 * a[i][j];
      }
      linear(*this, coef, cells, IRT_LQ, rowTotal);
    }

    // every column sums to a non-negative number: sum_i a[i][j] * (1 - 2 cellFlip) >= 0
    for (int j = 0; j < cols; ++j) {
      int colTotal = 0;
      BoolVarArgs cells;
      IntArgs coef(rows);
      for (int i = 0; i < rows; ++i) {
        colTotal += a[i][j];
        cells << cellFlip[i * cols + j];
        coef[i] = 2 * a[i][j];
      }
      linear(*this, coef, cells, IRT_LQ, colTotal);
    }

    // the overall sum after the flips is the sum of all entries times their signs
    IntArgs allCoef(rows * cols);
    BoolVarArgs allCells;
    int matrixTotal = 0;
    for (int i = 0; i < rows; ++i)
      for (int j = 0; j < cols; ++j) {
        matrixTotal += a[i][j];
        allCells << cellFlip[i * cols + j];
        allCoef[i * cols + j] = -2 * a[i][j];
      }
    total = expr(*this, sum(allCoef, allCells) + matrixTotal);

    // branch on the column flips first: once they are fixed, each row's sign is
    // forced to make its sum non-negative, so the row flips follow by propagation
    branch(*this, colFlip, BOOL_VAR_NONE(), BOOL_VAL_MIN());
    branch(*this, rowFlip, BOOL_VAR_NONE(), BOOL_VAL_MIN());

    minimize(total);
    output("row_signs", rowSign);
    output("col_signs", colSign);
  }

  FlipRowsCols(FlipRowsCols& s) : dcp::Space(s), rows(s.rows), cols(s.cols) {
    rowFlip.update(*this, s.rowFlip);
    colFlip.update(*this, s.colFlip);
    cellFlip.update(*this, s.cellFlip);
    rowSign.update(*this, s.rowSign);
    colSign.update(*this, s.colSign);
    total.update(*this, s.total);
  }
  Gecode::Space* copy() override { return new FlipRowsCols(*this); }
};

DCP_MODEL(FlipRowsCols)
