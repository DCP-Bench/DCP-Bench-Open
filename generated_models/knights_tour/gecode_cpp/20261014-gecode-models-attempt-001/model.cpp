// Knight's tour: visit every square of an n x n chessboard exactly once with
// knight moves, numbering the squares by move (0 to n*n-1). The tour is open:
// it does not return to the starting square.
//
// Squares are cells c = i*n + j. succ[c] is the square visited after c. A
// closing node (index n*n) stands for the gap between the last and the first
// square, so the open tour becomes one circuit over n*n+1 nodes. rank[c] is the
// move number of square c.

#include <algorithm>
#include <vector>

#include "dcp.h"

class KnightsTour : public dcp::Space {
 protected:
  int n;
  int cells;            // n*n squares
  IntVarArray succ;     // succ[c] for squares c, succ[cells] for the closing node
  IntVarArray rank;     // rank[c]: move number of square c

 public:
  explicit KnightsTour(const json& instance)
      : n(instance.at("n").get<int>()), cells(n * n) {
    // A knight moves 2 steps in one direction and 1 in the other (8 offsets).
    static const int dr[8] = {1, 2, 2, 1, -1, -2, -2, -1};
    static const int dc[8] = {2, 1, -1, -2, -2, -1, 1, 2};

    // a square's successor is one of the squares a knight move reaches from it,
    // or the closing node when the square is the last one of the tour
    IntVarArgs next;
    for (int i = 0; i < n; ++i)
      for (int j = 0; j < n; ++j) {
        std::vector<int> to;
        for (int k = 0; k < 8; ++k) {
          int a = i + dr[k], b = j + dc[k];
          if (a >= 0 && a < n && b >= 0 && b < n) to.push_back(a * n + b);
        }
        to.push_back(cells);
        std::sort(to.begin(), to.end());
        next << IntVar(*this, IntSet(IntArgs(to)));
      }
    // the closing node is followed by the first square, which can be any square
    next << IntVar(*this, 0, cells - 1);
    succ = IntVarArray(*this, next);

    // the tour visits every square once: one circuit through all squares and the closing node
    IntVarArgs circ;
    for (int c = 0; c <= cells; ++c) circ << succ[c];
    circuit(*this, circ, IPL_DOM);

    // move numbers run from 0 to n*n-1
    rank = IntVarArray(*this, cells, 0, cells - 1);

    // each knight move goes to the square numbered one higher, unless the square
    // is the last one. rankOf is rank with a spare entry for the closing node;
    // element reads the rank of the successor
    IntVarArgs rankOf;
    for (int c = 0; c < cells; ++c) rankOf << rank[c];
    rankOf << IntVar(*this, 0, cells - 1);
    for (int c = 0; c < cells; ++c) {
      IntVar after(*this, 0, cells - 1);
      element(*this, rankOf, succ[c], after);
      rel(*this, (succ[c] == cells) || (after == rank[c] + 1));
    }

    // the first square, the successor of the closing node, is numbered 0
    for (int c = 0; c < cells; ++c) rel(*this, (succ[cells] != c) || (rank[c] == 0));

    // branch on the tour (fewest moves first), then read off the move numbers
    branch(*this, succ, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    branch(*this, rank, INT_VAR_NONE(), INT_VAL_MIN());

    // x[i][j] is the move number of square (i, j)
    Matrix<IntVarArray> board(rank, n, n);
    output("x", board);
  }

  KnightsTour(KnightsTour& s) : dcp::Space(s), n(s.n), cells(s.cells) {
    succ.update(*this, s.succ);
    rank.update(*this, s.rank);
  }

  Gecode::Space* copy() override { return new KnightsTour(*this); }
};

DCP_MODEL(KnightsTour)
