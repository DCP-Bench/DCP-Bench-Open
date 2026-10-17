// Knight's tour on an n x n chessboard: a sequence of knight moves that visits every
// square exactly once, without returning to the start. x[i][j] is the move number
// (0 to n*n-1) at which the knight visits square (i, j).
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int n = instance.at("n").get<int>();
  int squares = n * n;
  double big = squares;  // bounds every difference of two move numbers

  // pos[s] = the move number of square s = i * n + j, from 0 to n*n-1
  std::vector<dcp::Lin> pos(squares);
  for (int s = 0; s < squares; ++s) pos[s] = dcp::new_var(h, 0, squares - 1);

  // the knight moves in an L shape: two squares in one direction and one across
  static const int dr[8] = {1, 2, 2, 1, -1, -2, -2, -1};
  static const int dc[8] = {2, 1, -1, -2, -2, -1, 1, 2};

  // arc from square s to square t: the knight goes from s to t at the next move
  struct Arc {
    int from;
    int to;
    dcp::Lin use;
  };
  std::vector<Arc> arcs;
  std::vector<dcp::Lin> leaving(squares);
  std::vector<dcp::Lin> entering(squares);
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; ++j)
      for (int d = 0; d < 8; ++d) {
        int r = i + dr[d];
        int c = j + dc[d];
        if (r < 0 || r >= n || c < 0 || c >= n) continue;
        int s = i * n + j;
        int t = r * n + c;
        dcp::Lin use = dcp::new_var(h, 0, 1);
        arcs.push_back({s, t, use});
        leaving[s] = leaving[s] + use;
        entering[t] = entering[t] + use;
      }

  // a square is left by at most one move, and entered by at most one move
  for (int s = 0; s < squares; ++s) {
    dcp::add_row(h, leaving[s], -kHighsInf, 1);
    dcp::add_row(h, entering[s], -kHighsInf, 1);
  }

  // the tour makes one move fewer than it has squares: exactly one square is never left
  dcp::Lin all_moves;
  for (const Arc& a : arcs) all_moves = all_moves + a.use;
  dcp::add_row(h, all_moves, squares - 1, squares - 1);

  // a square that is not entered by any move is the start, at move number 0
  for (int s = 0; s < squares; ++s)
    dcp::add_row(h, pos[s] - (big - 1) * entering[s], -kHighsInf, 0);

  // if a move goes from s to t, then t is the move right after s
  for (const Arc& a : arcs) {
    dcp::add_row(h, pos[a.to] - pos[a.from] - big * a.use, 1 - big, kHighsInf);
    dcp::add_row(h, pos[a.to] - pos[a.from] + big * a.use, -kHighsInf, 1 + big);
  }

  // x[i][j] = the move number of square (i, j)
  std::vector<std::vector<dcp::Lin>> x(n, std::vector<dcp::Lin>(n));
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; ++j) x[i][j] = pos[i * n + j];
  out.add("x", x);
}
