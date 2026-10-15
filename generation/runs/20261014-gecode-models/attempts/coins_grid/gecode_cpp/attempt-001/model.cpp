#include "dcp.h"

#include <algorithm>
#include <numeric>

// Coins grid: place coins on an n by n grid so that every row and every column
// holds exactly c coins and each cell holds at most one coin. Minimise the sum,
// over all cells that hold a coin, of the squared horizontal distance (j - i)^2
// of the cell from the main diagonal.
class CoinsGrid : public dcp::Space {
 protected:
  BoolVarArray x;  // x[i*n + j] = 1 if cell (i, j) holds a coin
  IntVar z;        // sum of the squared distances from the main diagonal of the coins

 public:
  explicit CoinsGrid(const json& instance) {
    // n and c come from the instance, not from the example
    int n = instance.at("n").get<int>();
    int c = instance.at("c").get<int>();

    x = BoolVarArray(*this, n * n, 0, 1);

    // in each row exactly c coins must be placed
    for (int i = 0; i < n; ++i) {
      BoolVarArgs row;
      for (int j = 0; j < n; ++j) row << x[i * n + j];
      linear(*this, row, IRT_EQ, c, IPL_DOM);
    }

    // in each column exactly c coins must be placed
    for (int j = 0; j < n; ++j) {
      BoolVarArgs col;
      for (int i = 0; i < n; ++i) col << x[i * n + j];
      linear(*this, col, IRT_EQ, c, IPL_DOM);
    }

    // at most one coin in each cell: each cell is a single Boolean, so nothing to post

    // the cost of a coin in cell (i, j) is the squared horizontal distance (j - i)^2
    // from the main diagonal. z is the total cost over all coins. It is split per row
    // and per column, so each row (column) cost has its own bounds: the c cheapest
    // and the c dearest cells of that row (column). The split gives a stronger bound
    // than one sum over the grid.
    std::vector<int> cost(n * n);
    for (int i = 0; i < n; ++i)
      for (int j = 0; j < n; ++j) cost[i * n + j] = (j - i) * (j - i);

    // lower bound on z: the cheapest c cells of each row, and of each column, summed
    int lo_rows = 0, lo_cols = 0, hi_total = 0;
    IntVarArgs rowcost, colcost;
    for (int i = 0; i < n; ++i) {
      IntArgs wi(n);
      BoolVarArgs ri;
      std::vector<int> cs;
      for (int j = 0; j < n; ++j) {
        wi[j] = cost[i * n + j];
        ri << x[i * n + j];
        cs.push_back(cost[i * n + j]);
      }
      std::sort(cs.begin(), cs.end());
      int lo = 0, hi = 0;
      for (int k = 0; k < c; ++k) { lo += cs[k]; hi += cs[n - 1 - k]; }
      lo_rows += lo;
      hi_total += hi;
      IntVar rc(*this, lo, hi);
      linear(*this, wi, ri, IRT_EQ, rc, IPL_BND);
      rowcost << rc;
    }
    for (int j = 0; j < n; ++j) {
      IntArgs wj(n);
      BoolVarArgs cj;
      std::vector<int> cs;
      for (int i = 0; i < n; ++i) {
        wj[i] = cost[i * n + j];
        cj << x[i * n + j];
        cs.push_back(cost[i * n + j]);
      }
      std::sort(cs.begin(), cs.end());
      int lo = 0, hi = 0;
      for (int k = 0; k < c; ++k) { lo += cs[k]; hi += cs[n - 1 - k]; }
      lo_cols += lo;
      IntVar cc(*this, lo, hi);
      linear(*this, wj, cj, IRT_EQ, cc, IPL_BND);
      colcost << cc;
    }
    z = IntVar(*this, std::max(lo_rows, lo_cols), hi_total);
    linear(*this, rowcost, IRT_EQ, z, IPL_BND);
    linear(*this, colcost, IRT_EQ, z, IPL_BND);

    // branch on the cheapest cells first, placing coins there before the others
    std::vector<int> order(n * n);
    std::iota(order.begin(), order.end(), 0);
    std::stable_sort(order.begin(), order.end(),
                     [&](int a, int b) { return cost[a] < cost[b]; });
    BoolVarArgs ordered;
    for (int k : order) ordered << x[k];
    branch(*this, ordered, BOOL_VAR_AFC_MAX(0.99), BOOL_VAL_MAX());

    // minimise the total squared distance of the coins from the main diagonal
    minimize(z);
    // learning from failures needs restarts to pay off
    restarts(100);

    // outputs: x is the grid row by row, z the total cost
    std::vector<BoolVarArgs> rows(n);
    for (int i = 0; i < n; ++i)
      for (int j = 0; j < n; ++j) rows[i] << x[i * n + j];
    output("x", rows);
    output("z", z);
  }

  CoinsGrid(CoinsGrid& s) : dcp::Space(s) {
    x.update(*this, s.x);
    z.update(*this, s.z);
  }

  Gecode::Space* copy() override { return new CoinsGrid(*this); }
};

DCP_MODEL(CoinsGrid)
