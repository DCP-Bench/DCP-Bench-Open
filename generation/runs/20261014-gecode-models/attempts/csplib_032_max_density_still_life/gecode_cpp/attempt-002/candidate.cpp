#include "dcp.h"

// Maximum density still life: place live and dead cells on an n x m grid so that
// the pattern is a still life (it does not change from one generation to the next)
// and the number of live cells is as large as possible. Cells outside the grid
// are dead, and they take part in the rules.
class MaxDensityStillLife : public dcp::Space {
 protected:
  int n, m;
  BoolVarArray cell;  // cell[r * m + c] = 1 if the cell in row r, column c is alive
  IntVar live;        // number of live cells

 public:
  explicit MaxDensityStillLife(const json& instance) {
    n = instance.at("n").get<int>();
    m = instance.at("m").get<int>();
    cell = BoolVarArray(*this, n * m, 0, 1);

    auto at = [&](int r, int c) { return cell[r * m + c]; };

    // the live neighbours of (r, c) that lie inside the grid
    auto neighbours = [&](int r, int c) {
      BoolVarArgs nb;
      for (int dr = -1; dr <= 1; ++dr)
        for (int dc = -1; dc <= 1; ++dc) {
          if (dr == 0 && dc == 0) continue;
          int rr = r + dr, cc = c + dc;
          if (rr >= 0 && rr < n && cc >= 0 && cc < m) nb << at(rr, cc);
        }
      return nb;
    };

    // every cell of the grid and every dead cell just outside it
    for (int r = -1; r <= n; ++r)
      for (int c = -1; c <= m; ++c) {
        BoolVarArgs nb = neighbours(r, c);
        bool inside = r >= 0 && r < n && c >= 0 && c < m;

        if (!inside) {
          // a dead cell outside the grid must not have exactly 3 live neighbours
          linear(*this, nb, IRT_NQ, 3);
          continue;
        }

        BoolVar x = at(r, c);
        BoolVarArgs both(nb);
        both << x;

        // a live cell has at least 2 live neighbours: sum(nb) - 2x >= 0
        IntArgs lo = IntArgs::create(both.size(), 1, 0);
        lo[both.size() - 1] = -2;
        linear(*this, lo, both, IRT_GQ, 0);

        // a live cell has at most 3 live neighbours: sum(nb) + 5x <= 8
        IntArgs hi = IntArgs::create(both.size(), 1, 0);
        hi[both.size() - 1] = 5;
        linear(*this, hi, both, IRT_LQ, 8);

        // a dead cell must not have exactly 3 live neighbours: sum(nb) == 3 implies x = 1
        linear(*this, nb, IRT_EQ, 3, Reify(x, RM_PMI));
      }

    // maximise the number of live cells
    live = expr(*this, sum(cell));
    maximize(live);

    branch(*this, cell, BOOL_VAR_NONE(), BOOL_VAL_MAX());
    // cells are decided in reading order, a live cell first

    // the grid, one list per row
    std::vector<BoolVarArgs> rows(n);
    for (int r = 0; r < n; ++r)
      for (int c = 0; c < m; ++c) rows[r] << at(r, c);
    output("grid", rows);
  }

  MaxDensityStillLife(MaxDensityStillLife& s) : dcp::Space(s), n(s.n), m(s.m) {
    cell.update(*this, s.cell);
    live.update(*this, s.live);
  }
  Gecode::Space* copy() override { return new MaxDensityStillLife(*this); }
};

DCP_MODEL(MaxDensityStillLife)
