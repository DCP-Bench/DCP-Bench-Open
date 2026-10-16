// Knight's tour: a knight visits every square of an n x n board exactly once; x[r][c] is
// the move number (0 to n*n-1) at which the knight is on square (r, c). The tour does not
// need to return to its start.
#include "dcp.h"

#include <utility>
#include <vector>

void Build(const json& instance, json& outputs) {
  int n = instance.at("n");   // board size
  int cells = n * n;          // number of squares, also the number of moves
  int dummy = cells;          // extra node: an open tour is a circuit through the dummy

  // the knight's moves as (row, column) offsets
  std::vector<std::pair<int, int>> steps = {{1, 2},  {2, 1},  {2, -1},  {1, -2},
                                            {-1, -2}, {-2, -1}, {-2, 1}, {-1, 2}};

  // square index p = r * n + c; neighbours[p] lists the squares one knight's move away
  std::vector<std::vector<int>> neighbours(cells);
  for (int r = 0; r < n; ++r) {
    for (int c = 0; c < n; ++c) {
      for (auto& s : steps) {
        int r2 = r + s.first;
        int c2 = c + s.second;
        if (r2 < 0 || r2 >= n || c2 < 0 || c2 >= n) continue;
        neighbours[r * n + c].push_back(r2 * n + c2);
      }
    }
  }

  // succ[p] is the square visited after square p; succ[dummy] is the first square of the tour
  // and the square that goes to the dummy is the last one
  vec<IntVar*> succ;
  createVars(succ, cells + 1, 0, cells);

  // the successors form one circuit through all squares and the dummy
  circuit(succ);

  // a square is followed by a knight's move, or by the dummy when it is the last square
  for (int p = 0; p < cells; ++p) {
    vec<vec<int>> allowed;
    for (int q : neighbours[p]) {
      allowed.push();
      allowed.last().push(q);
    }
    allowed.push();
    allowed.last().push(dummy);
    vec<IntVar*> one;
    one.push(succ[p]);
    table(one, allowed);
  }

  // move[p] is the move number at square p
  vec<IntVar*> move;
  createVars(move, cells, 0, cells - 1);

  // the knight visits every square exactly once, so the move numbers are all different
  all_different(move);

  // the first square of the tour is move 0 and the moves count up along the tour:
  // if square q follows square p, then move[q] = move[p] + 1 (for the squares not after the dummy)
  for (int p = 0; p < cells; ++p) {
    for (int q : neighbours[p]) {
      BoolView follows = newBoolVar();
      int_rel_reif(succ[p], IRT_EQ, q, follows);
      int_rel_half_reif(move[q], IRT_EQ, move[p], follows, 1);
    }
  }

  // the tour starts on the square the dummy points to: that square has move 0
  for (int p = 0; p < cells; ++p) {
    BoolView starts = newBoolVar();
    int_rel_reif(succ[dummy], IRT_EQ, p, starts);
    int_rel_half_reif(move[p], IRT_EQ, 0, starts);
  }

  // branch on the successors, smallest square first
  branch(succ, VAR_SIZE_MIN, VAL_MIN);

  json board = json::array();
  for (int r = 0; r < n; ++r) {
    json rowOut = json::array();
    for (int c = 0; c < n; ++c) rowOut.push_back(dcp::out(move[r * n + c]));
    board.push_back(rowOut);
  }
  outputs = {{"x", board}};
}
