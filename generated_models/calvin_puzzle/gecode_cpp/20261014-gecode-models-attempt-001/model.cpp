#include "dcp.h"

// Calvin puzzle: fill an n by n grid with the numbers 1..n^2, each square getting one
// number. The next number is placed either exactly three squares away horizontally or
// vertically, or exactly two squares away diagonally, from the previous one.
class CalvinPuzzle : public dcp::Space {
 protected:
  IntVarArray pos;  // pos[k]: square (row-major index) holding the number k+1
  IntVarArray g;    // g[c]: number in square c, minus one
  IntVarArray x;    // x[c]: number in square c

 public:
  explicit CalvinPuzzle(const json& instance) {
    int n = instance.at("n").get<int>();
    int N = n * n;

    pos = IntVarArray(*this, N, 0, N - 1);
    g = IntVarArray(*this, N, 0, N - 1);
    x = IntVarArray(*this, N, 1, N);

    // every square holds exactly one number, and every number is in exactly one square
    channel(*this, g, pos, IPL_DOM);
    distinct(*this, pos, IPL_DOM);

    // the grid shows the numbers 1..N (g is the zero-based view used by channel)
    for (int c = 0; c < N; ++c) rel(*this, x[c] == g[c] + 1);

    // allowed moves between square a and square b: exactly three squares away in a row
    // or column (a two-square gap), or exactly two squares away diagonally (a one-square gap)
    TupleSet moves(2);
    for (int a = 0; a < N; ++a)
      for (int b = 0; b < N; ++b) {
        int dr = a / n > b / n ? a / n - b / n : b / n - a / n;
        int dc = a % n > b % n ? a % n - b % n : b % n - a % n;
        if ((dr == 3 && dc == 0) || (dr == 0 && dc == 3) || (dr == 2 && dc == 2))
          moves.add(IntArgs({a, b}));
      }
    moves.finalize();

    // each number is placed by one of those moves from the previous number
    for (int k = 0; k + 1 < N; ++k) {
      IntVarArgs step;
      step << pos[k] << pos[k + 1];
      extensional(*this, step, moves);
    }

    // search: place the numbers in order, most constrained next square first
    branch(*this, pos, INT_VAR_AFC_SIZE_MAX(0.99), INT_VAL_MIN());
    restarts(100);

    Matrix<IntVarArray> grid(x, n, n);
    output("x", grid);
  }

  CalvinPuzzle(CalvinPuzzle& s) : dcp::Space(s) {
    pos.update(*this, s.pos);
    g.update(*this, s.g);
    x.update(*this, s.x);
  }
  Gecode::Space* copy() override { return new CalvinPuzzle(*this); }
};

DCP_MODEL(CalvinPuzzle)
