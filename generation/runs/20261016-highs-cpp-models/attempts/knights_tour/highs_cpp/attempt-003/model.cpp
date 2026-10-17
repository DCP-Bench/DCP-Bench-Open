// Knight's tour on an n x n chessboard: a sequence of knight moves that visits every
// square exactly once, without returning to the starting square. x[i][j] is the move number
// (0 to n*n-1) at which the knight visits square (i, j).
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int n = instance.at("n").get<int>();
  int N = n * n;

  static const int dr[8] = {1, 2, 2, 1, -1, -2, -2, -1};
  static const int dc[8] = {2, 1, -1, -2, -2, -1, 1, 2};
  std::vector<std::vector<int>> adj(N);
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; ++j)
      for (int d = 0; d < 8; ++d) {
        int r = i + dr[d], c = j + dc[d];
        if (r < 0 || r >= n || c < 0 || c >= n) continue;
        adj[i * n + j].push_back(r * n + c);
      }

  // the tour is a Hamiltonian path in the knight graph: arc[s][t] = 1 when the knight moves
  // from square s to square t; start[s] / last[s] mark the first and the last square
  std::vector<std::vector<dcp::Lin>> arc(N, std::vector<dcp::Lin>(N));
  std::vector<dcp::Lin> start(N), last(N), pos(N);
  for (int s = 0; s < N; ++s) {
    for (int t : adj[s]) arc[s][t] = dcp::new_var(h, 0, 1);
    start[s] = dcp::new_var(h, 0, 1);
    last[s] = dcp::new_var(h, 0, 1);
    pos[s] = dcp::new_var(h, 0, N - 1);
  }

  // the knight visits every square exactly once: each square is left by one move or is the
  // last square, and entered by one move or is the first square
  for (int s = 0; s < N; ++s) {
    dcp::Lin leaving = last[s];
    for (int t : adj[s]) leaving = leaving + arc[s][t];
    dcp::add_row(h, leaving, 1, 1);
    dcp::Lin entering = start[s];
    for (int t : adj[s]) entering = entering + arc[t][s];
    dcp::add_row(h, entering, 1, 1);
  }
  // one first square and one last square
  {
    dcp::Lin a, b;
    for (int s = 0; s < N; ++s) { a = a + start[s]; b = b + last[s]; }
    dcp::add_row(h, a, 1, 1);
    dcp::add_row(h, b, 1, 1);
  }

  // the move numbers: the first square has number 0, and a move from s to t raises the number
  // by at least one (this also rules out separate cycles); numbers are within 0 .. n*n-1
  for (int s = 0; s < N; ++s) {
    dcp::add_row(h, pos[s] + (double)(N - 1) * start[s], 0, (double)(N - 1));
    dcp::add_row(h, pos[s] + start[s], 1, kHighsInf);
    dcp::add_row(h, pos[s] - (double)(N - 1) * last[s], 0, kHighsInf);
  }
  for (int s = 0; s < N; ++s)
    for (int t : adj[s])
      dcp::add_row(h, pos[t] - pos[s] - (double)N * arc[s][t], 1 - N, kHighsInf);

  std::vector<std::vector<dcp::Lin>> x(n, std::vector<dcp::Lin>(n));
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; ++j) x[i][j] = pos[i * n + j];
  out.add("x", x);
}
