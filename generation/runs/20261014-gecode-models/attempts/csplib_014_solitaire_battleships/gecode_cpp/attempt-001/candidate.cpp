#include "dcp.h"

// Battleships (solitaire battleships, CSPLib 014): place a fleet of horizontal and
// vertical ships on a grid so that the row and column counts of occupied squares
// hold, the fleet composition holds, and no two ships touch, not even diagonally.
// Each square is water, a submarine, or one part of a ship (left, right, top, bottom
// or middle). Some squares are given as hints.
class Battleships : public dcp::Space {
 protected:
  int rows_, cols_;
  IntVarArray g_;  // (rows + 2) x (cols + 2) grid with a water border, row-major

  int idx(int r, int c) const { return (r + 1) * (cols_ + 2) + (c + 1); }

 public:
  explicit Battleships(const json& inst)
      : rows_(inst.at("rows").get<int>()), cols_(inst.at("cols").get<int>()) {
    const int R = rows_, C = cols_;
    // Square codes come from the instance.
    const int WATER = inst.at("WATER").get<int>();
    const int SHIP = inst.at("_SHIP").get<int>();
    const int SUB = inst.at("CIRCLE").get<int>();
    const int LEFT = inst.at("LEFT").get<int>();
    const int RIGHT = inst.at("RIGHT").get<int>();
    const int TOP = inst.at("TOP").get<int>();
    const int BOTTOM = inst.at("BOTTOM").get<int>();
    const int MIDDLE = inst.at("MIDDLE").get<int>();

    g_ = IntVarArray(*this, (R + 2) * (C + 2), 0, MIDDLE);
    for (int r = -1; r <= R; ++r)
      for (int c = -1; c <= C; ++c) {
        if (r < 0 || r >= R || c < 0 || c >= C) {
          // outside the grid counts as water
          rel(*this, g_[idx(r, c)], IRT_EQ, WATER);
        } else {
          // the generic ship marker is not a square of the solution
          rel(*this, g_[idx(r, c)], IRT_NQ, SHIP);
        }
      }

    // neighbour of square (r, c) at offset (dr, dc)
    auto v = [&](int r, int c, int dr, int dc) { return g_[idx(r + dr, c + dc)]; };

    for (int r = 0; r < R; ++r)
      for (int c = 0; c < C; ++c) {
        // no two ships touch, not even diagonally: a ship square has water on its diagonals
        rel(*this, (v(r, c, 0, 0) == WATER) ||
                       ((v(r, c, -1, -1) == WATER) && (v(r, c, -1, 1) == WATER) &&
                        (v(r, c, 1, -1) == WATER) && (v(r, c, 1, 1) == WATER)));

        // a submarine is one square surrounded by water
        rel(*this, (v(r, c, 0, 0) == SUB) >>
                       ((v(r, c, -1, 0) == WATER) && (v(r, c, 1, 0) == WATER) &&
                        (v(r, c, 0, -1) == WATER) && (v(r, c, 0, 1) == WATER)));

        // the left end of a horizontal ship: water to the left, above and below, ship part to the right
        rel(*this, (v(r, c, 0, 0) == LEFT) >>
                       ((v(r, c, 0, -1) == WATER) && (v(r, c, -1, 0) == WATER) &&
                        (v(r, c, 1, 0) == WATER) &&
                        ((v(r, c, 0, 1) == RIGHT) || (v(r, c, 0, 1) == MIDDLE))));

        // the right end of a horizontal ship: water to the right, above and below, ship part to the left
        rel(*this, (v(r, c, 0, 0) == RIGHT) >>
                       ((v(r, c, 0, 1) == WATER) && (v(r, c, -1, 0) == WATER) &&
                        (v(r, c, 1, 0) == WATER) &&
                        ((v(r, c, 0, -1) == LEFT) || (v(r, c, 0, -1) == MIDDLE))));

        // the top end of a vertical ship: water above, left and right, ship part below
        rel(*this, (v(r, c, 0, 0) == TOP) >>
                       ((v(r, c, -1, 0) == WATER) && (v(r, c, 0, -1) == WATER) &&
                        (v(r, c, 0, 1) == WATER) &&
                        ((v(r, c, 1, 0) == BOTTOM) || (v(r, c, 1, 0) == MIDDLE))));

        // the bottom end of a vertical ship: water below, left and right, ship part above
        rel(*this, (v(r, c, 0, 0) == BOTTOM) >>
                       ((v(r, c, 1, 0) == WATER) && (v(r, c, 0, -1) == WATER) &&
                        (v(r, c, 0, 1) == WATER) &&
                        ((v(r, c, -1, 0) == TOP) || (v(r, c, -1, 0) == MIDDLE))));

        // a middle square lies in a horizontal ship (ship parts left and right, water above and below)
        // or in a vertical ship (ship parts above and below, water left and right)
        BoolExpr horizontal = ((v(r, c, 0, -1) == LEFT) || (v(r, c, 0, -1) == MIDDLE)) &&
                              ((v(r, c, 0, 1) == RIGHT) || (v(r, c, 0, 1) == MIDDLE)) &&
                              (v(r, c, -1, 0) == WATER) && (v(r, c, 1, 0) == WATER);
        BoolExpr vertical = ((v(r, c, -1, 0) == TOP) || (v(r, c, -1, 0) == MIDDLE)) &&
                            ((v(r, c, 1, 0) == BOTTOM) || (v(r, c, 1, 0) == MIDDLE)) &&
                            (v(r, c, 0, -1) == WATER) && (v(r, c, 0, 1) == WATER);
        rel(*this, (v(r, c, 0, 0) == MIDDLE) >> (horizontal || vertical));
      }

    // the number of occupied squares in each row and column
    const auto& rowsum = inst.at("rowsum");
    const auto& colsum = inst.at("colsum");
    for (int r = 0; r < R; ++r) {
      IntVarArgs row;
      for (int c = 0; c < C; ++c) row << g_[idx(r, c)];
      count(*this, row, WATER, IRT_EQ, C - rowsum[r].get<int>());
    }
    for (int c = 0; c < C; ++c) {
      IntVarArgs col;
      for (int r = 0; r < R; ++r) col << g_[idx(r, c)];
      count(*this, col, WATER, IRT_EQ, R - colsum[c].get<int>());
    }

    // the fleet: fleet_counts lists [length, number of ships of that length]
    int chains = 0;
    for (const auto& entry : inst.at("fleet_counts")) {
      const int len = entry[0].get<int>();
      const int num = entry[1].get<int>();
      if (len == 1) {
        // a submarine is a single square
        IntVarArgs subs;
        for (int r = 0; r < R; ++r)
          for (int c = 0; c < C; ++c) subs << g_[idx(r, c)];
        count(*this, subs, SUB, IRT_EQ, num);
      } else {
        // a ship of this length is an exact window: an end, len-2 middles, the other end
        chains += num;
        BoolVarArgs hits;
        for (int r = 0; r < R; ++r)
          for (int c = 0; c + len <= C; ++c) {
            BoolExpr across = (v(r, c, 0, 0) == LEFT);
            for (int i = 1; i < len - 1; ++i) across = across && (v(r, c + i, 0, 0) == MIDDLE);
            across = across && (v(r, c + len - 1, 0, 0) == RIGHT);
            hits << expr(*this, across);
          }
        for (int c = 0; c < C; ++c)
          for (int r = 0; r + len <= R; ++r) {
            BoolExpr down = (v(r, c, 0, 0) == TOP);
            for (int i = 1; i < len - 1; ++i) down = down && (v(r + i, c, 0, 0) == MIDDLE);
            down = down && (v(r + len - 1, c, 0, 0) == BOTTOM);
            hits << expr(*this, down);
          }
        linear(*this, hits, IRT_EQ, num);
      }
    }

    // every ship of length two or more has exactly one left or top end
    BoolVarArgs ends;
    for (int r = 0; r < R; ++r)
      for (int c = 0; c < C; ++c) {
        ends << expr(*this, v(r, c, 0, 0) == LEFT);
        ends << expr(*this, v(r, c, 0, 0) == TOP);
      }
    linear(*this, ends, IRT_EQ, chains);

    // the given squares
    for (const auto& h : inst.at("hints"))
      rel(*this, g_[idx(h[0].get<int>(), h[1].get<int>())], IRT_EQ, h[2].get<int>());

    // branch on every square of the grid
    IntVarArgs all;
    for (int r = 0; r < R; ++r)
      for (int c = 0; c < C; ++c) all << g_[idx(r, c)];
    branch(*this, all, INT_VAR_SIZE_MIN(), INT_VAL_MIN());

    // the solution: the grid of squares, row by row
    std::vector<IntVarArgs> grid(R);
    for (int r = 0; r < R; ++r)
      for (int c = 0; c < C; ++c) grid[r] << g_[idx(r, c)];
    output("grid", grid);
  }

  Battleships(Battleships& s) : dcp::Space(s), rows_(s.rows_), cols_(s.cols_) {
    g_.update(*this, s.g_);
  }
  Gecode::Space* copy() override { return new Battleships(*this); }
};

DCP_MODEL(Battleships)
