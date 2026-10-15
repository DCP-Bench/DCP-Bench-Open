#include <cstdlib>
#include "dcp.h"

// N-Puzzle: trace a sliding-tile puzzle from its start state to its end state in
// exactly N_STEPS states (start and end included). Tile 0 is the blank. Each step
// slides one tile into the blank, so the blank moves to a neighbouring cell, and the
// state changes at every step (no freezing).
class NPuzzle : public dcp::Space {
 protected:
  int side;        // the grid is side x side, read from puzzle_start
  int cells;       // side * side cells and tiles 0..cells-1
  int steps;       // N_STEPS
  IntVarArray tile;  // tile[t * cells + c]: tile on cell c in state t
  IntVarArray where; // where[t * cells + v]: cell of tile v in state t (inverse of tile)

  int idx(int t, int c) const { return t * cells + c; }

 public:
  explicit NPuzzle(const json& instance) {
    std::vector<std::vector<int>> start_grid =
        instance.at("puzzle_start").get<std::vector<std::vector<int>>>();
    std::vector<std::vector<int>> end_grid =
        instance.at("puzzle_end").get<std::vector<std::vector<int>>>();
    steps = instance.at("N_STEPS").get<int>();
    side = static_cast<int>(start_grid.size());
    cells = side * side;

    tile = IntVarArray(*this, steps * cells, 0, cells - 1);
    where = IntVarArray(*this, steps * cells, 0, cells - 1);

    // each state is an arrangement of the tiles: tile and where are inverse permutations
    for (int t = 0; t < steps; ++t) {
      IntVarArgs on_cell, of_tile;
      for (int c = 0; c < cells; ++c) on_cell << tile[idx(t, c)];
      for (int v = 0; v < cells; ++v) of_tile << where[idx(t, v)];
      distinct(*this, on_cell, IPL_DOM);
      channel(*this, on_cell, of_tile, IPL_DOM);
    }

    // the first state is the puzzle start, the last state is the puzzle end
    for (int r = 0; r < side; ++r)
      for (int c = 0; c < side; ++c) {
        rel(*this, tile[idx(0, r * side + c)] == start_grid[r][c]);
        rel(*this, tile[idx(steps - 1, r * side + c)] == end_grid[r][c]);
      }

    // a step slides a tile into the blank: the blank moves to a neighbouring cell
    TupleSet neighbours(2);
    for (int r = 0; r < side; ++r)
      for (int c = 0; c < side; ++c) {
        if (r + 1 < side) {
          neighbours.add(IntArgs({r * side + c, (r + 1) * side + c}));
          neighbours.add(IntArgs({(r + 1) * side + c, r * side + c}));
        }
        if (c + 1 < side) {
          neighbours.add(IntArgs({r * side + c, r * side + c + 1}));
          neighbours.add(IntArgs({r * side + c + 1, r * side + c}));
        }
      }
    neighbours.finalize();

    for (int t = 0; t + 1 < steps; ++t) {
      IntVarArgs blank_pair;
      blank_pair << where[idx(t, 0)] << where[idx(t + 1, 0)];
      extensional(*this, blank_pair, neighbours);

      IntVarArgs now, before;
      for (int c = 0; c < cells; ++c) {
        now << tile[idx(t + 1, c)];
        before << tile[idx(t, c)];
      }

      // the tile that slides into the old blank cell is the one on the new blank cell
      IntVar moved(*this, 0, cells - 1);
      element(*this, now, where[idx(t, 0)], moved);
      element(*this, before, where[idx(t + 1, 0)], moved);

      // every cell that is neither the old nor the new blank keeps its tile
      for (int c = 0; c < cells; ++c) {
        BoolVar keep = expr(*this, (where[idx(t, 0)] != c) && (where[idx(t + 1, 0)] != c));
        rel(*this, tile[idx(t + 1, c)], IRT_EQ, tile[idx(t, c)], imp(keep));
      }
    }

    // implied bound: a slide moves one tile one cell, so the total Manhattan distance of
    // the tiles to their end cells changes by exactly 1 per step and is 0 at the end
    std::vector<int> target_row(cells), target_col(cells);
    for (int r = 0; r < side; ++r)
      for (int c = 0; c < side; ++c) {
        int v = end_grid[r][c];
        target_row[v] = r;
        target_col[v] = c;
      }
    std::vector<IntArgs> distance;
    for (int c = 0; c < cells; ++c) {
      IntArgs d(cells);
      for (int v = 0; v < cells; ++v)
        d[v] = (v == 0) ? 0 : std::abs(c / side - target_row[v]) + std::abs(c % side - target_col[v]);
      distance.push_back(d);
    }
    for (int t = 0; t < steps; ++t) {
      IntVarArgs parts;
      for (int c = 0; c < cells; ++c) {
        IntVar d(*this, 0, 2 * side);
        element(*this, distance[c], tile[idx(t, c)], d);
        parts << d;
      }
      linear(*this, parts, IRT_LQ, steps - 1 - t);
    }

    // search: the blank path decides the states; then tiles and positions as fallback
    IntVarArgs blanks;
    for (int t = 0; t < steps; ++t) blanks << where[idx(t, 0)];
    branch(*this, blanks, INT_VAR_NONE(), INT_VAL_MIN());
    branch(*this, tile, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    branch(*this, where, INT_VAR_SIZE_MIN(), INT_VAL_MIN());

    // steps[t][r][c]: tile on row r, column c in state t
    std::vector<std::vector<IntVarArgs>> out(steps);
    for (int t = 0; t < steps; ++t) {
      out[t].resize(side);
      for (int r = 0; r < side; ++r)
        for (int c = 0; c < side; ++c) out[t][r] << tile[idx(t, r * side + c)];
    }
    output("steps", out);
  }

  NPuzzle(NPuzzle& s) : dcp::Space(s), side(s.side), cells(s.cells), steps(s.steps) {
    tile.update(*this, s.tile);
    where.update(*this, s.where);
  }
  Gecode::Space* copy() override { return new NPuzzle(*this); }
};

DCP_MODEL(NPuzzle)
