#include "dcp.h"

#include <algorithm>

// Cutting stock: cut raw rolls of width RollWidth according to a given list of
// cutting patterns, so that every width gets at least its ordered number of
// pieces, and minimise the total number of rolls cut.
class CuttingStock : public dcp::Space {
 protected:
  IntVarArray use;  // use[p]: number of rolls cut with pattern p
  IntVar total;     // total number of raw rolls cut

 public:
  explicit CuttingStock(const json& instance) {
    int np = instance.at("num_patterns").get<int>();
    std::vector<int> orders = instance.at("orders").get<std::vector<int>>();
    const json& pieces = instance.at("num_rolls_width");  // pieces[p][w]
    int nw = static_cast<int>(orders.size());

    // each pattern is used a number of times, with an upper bound from the data:
    // a pattern cutting width w needs at most ceil(orders[w] / pieces[p][w]) rolls
    // for that width, and using more rolls of it than the largest such value is
    // never necessary (one roll fewer still covers every width it cuts).
    IntVarArgs bounded;
    for (int p = 0; p < np; ++p) {
      int ub = 0;
      for (int w = 0; w < nw; ++w) {
        int k = pieces[p][w].get<int>();
        if (k > 0) ub = std::max(ub, (orders[w] + k - 1) / k);
      }
      bounded << IntVar(*this, 0, ub);
    }
    use = IntVarArray(*this, bounded);

    // for each width, the pieces cut from all rolls meet its orders:
    // sum over patterns of pieces[p][w] * use[p] >= orders[w]
    for (int w = 0; w < nw; ++w) {
      IntArgs cut_w(np);
      for (int p = 0; p < np; ++p) cut_w[p] = pieces[p][w].get<int>();
      linear(*this, cut_w, use, IRT_GQ, orders[w]);
    }

    // minimise the total number of raw rolls cut
    total = expr(*this, sum(use));
    minimize(total);

    // branch on the number of rolls per pattern, larger counts first
    branch(*this, use, INT_VAR_SIZE_MIN(), INT_VAL_MAX());

    output("min_rolls_cut", total);
    output("patterns_used", use);
  }

  CuttingStock(CuttingStock& s) : dcp::Space(s) {
    use.update(*this, s.use);
    total.update(*this, s.total);
  }
  Gecode::Space* copy() override { return new CuttingStock(*this); }
};

DCP_MODEL(CuttingStock)
