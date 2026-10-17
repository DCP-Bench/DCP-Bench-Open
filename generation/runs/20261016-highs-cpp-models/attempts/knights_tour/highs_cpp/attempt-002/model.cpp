// Knight's tour on an n x n chessboard: a sequence of knight moves that visits every
// square exactly once, without returning to the start. x[i][j] is the move number
// (0 to n*n-1) at which the knight visits square (i, j).
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int n = instance.at("n").get<int>();
  int squares = n * n;

  // square s = i * n + j has colour (i + j) mod 2. A knight move changes colour, so a square of
  // colour c is visited only at move numbers k with k mod 2 = c. The tour starts on colour 0:
  // on an odd board colour 0 is the majority colour, and on an even board reflecting a tour
  // swaps the colours, so no tour is lost.
  std::vector<int> colour(squares);
  for (int s = 0; s < squares; ++s) colour[s] = ((s / n) + (s % n)) % 2;

  // knight neighbours of each square
  static const int dr[8] = {1, 2, 2, 1, -1, -2, -2, -1};
  static const int dc[8] = {2, 1, -1, -2, -2, -1, 1, 2};
  std::vector<std::vector<int>> adj(squares);
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; ++j)
      for (int d = 0; d < 8; ++d) {
        int r = i + dr[d];
        int c = j + dc[d];
        if (r < 0 || r >= n || c < 0 || c >= n) continue;
        adj[i * n + j].push_back(r * n + c);
      }

  // number of knight moves from the corner (0, 0) to each square (breadth-first search)
  std::vector<int> dist(squares, -1);
  dist[0] = 0;
  std::vector<int> queue = {0};
  for (size_t q = 0; q < queue.size(); ++q)
    for (int t : adj[queue[q]])
      if (dist[t] < 0) {
        dist[t] = dist[queue[q]] + 1;
        queue.push_back(t);
      }

  // on[s][k] = 1 when square s is visited at move k; only for k of the square's colour and no
  // smaller than the knight distance from the start square
  std::vector<std::vector<bool>> exists(squares, std::vector<bool>(squares, false));
  std::vector<std::vector<dcp::Lin>> on(squares, std::vector<dcp::Lin>(squares));
  for (int s = 0; s < squares; ++s)
    for (int k = colour[s]; k < squares; k += 2) {
      if (k < dist[s]) continue;
      exists[s][k] = true;
      // the tour starts in the corner square (0, 0) at move 0, and by reflecting the board in
      // its diagonal the second square is (1, 2)
      double lower = (s == 0 && k == 0) || (s == 1 * n + 2 && k == 1) ? 1 : 0;
      on[s][k] = dcp::new_var(h, lower, 1);
    }

  // every square is visited at exactly one move
  for (int s = 0; s < squares; ++s) {
    dcp::Lin visits;
    for (int k = 0; k < squares; ++k)
      if (exists[s][k]) visits = visits + on[s][k];
    dcp::add_row(h, visits, 1, 1);
  }

  // every move number is made to exactly one square
  for (int k = 0; k < squares; ++k) {
    dcp::Lin who;
    for (int s = 0; s < squares; ++s)
      if (exists[s][k]) who = who + on[s][k];
    dcp::add_row(h, who, 1, 1);
  }

  // a square visited at move k is followed by a square a knight move away at move k + 1,
  // and a square visited at move k + 1 is preceded by a square a knight move away at move k
  for (int k = 0; k + 1 < squares; ++k) {
    for (int s = 0; s < squares; ++s) {
      if (!exists[s][k]) continue;
      dcp::Lin next;
      for (int t : adj[s])
        if (exists[t][k + 1]) next = next + on[t][k + 1];
      dcp::add_row(h, on[s][k] - next, -kHighsInf, 0);
    }
    for (int t = 0; t < squares; ++t) {
      if (!exists[t][k + 1]) continue;
      dcp::Lin prev;
      for (int s : adj[t])
        if (exists[s][k]) prev = prev + on[s][k];
      dcp::add_row(h, on[t][k + 1] - prev, -kHighsInf, 0);
    }
  }

  // next[s][t] = 1 when the move after square s goes to square t, a knight move away. Each square
  // has one next square, except the last one, and one previous square, except the start.
  std::vector<std::vector<dcp::Lin>> next(squares, std::vector<dcp::Lin>(squares));
  std::vector<std::pair<int, int>> edges;
  for (int s = 0; s < squares; ++s)
    for (int t : adj[s]) {
      next[s][t] = dcp::new_var(h, 0, 1);
      edges.push_back({s, t});
    }
  // a square visited at move k, followed by a square visited at move k + 1, uses that arc
  for (const auto& [s, t] : edges)
    for (int k = 0; k + 1 < squares; ++k)
      if (exists[s][k] && exists[t][k + 1])
        dcp::add_row(h, on[s][k] + on[t][k + 1] - next[s][t], -kHighsInf, 1);
  // each square leaves by one arc, or is the last square of the tour
  for (int s = 0; s < squares; ++s) {
    dcp::Lin leaving = exists[s][squares - 1] ? on[s][squares - 1] : dcp::Lin(0);
    for (int t : adj[s]) leaving = leaving + next[s][t];
    dcp::add_row(h, leaving, 1, 1);
  }
  // each square enters by one arc, or is the start square at move 0
  for (int t = 0; t < squares; ++t) {
    dcp::Lin entering = exists[t][0] ? on[t][0] : dcp::Lin(0);
    for (int s : adj[t]) entering = entering + next[s][t];
    dcp::add_row(h, entering, 1, 1);
  }

  // pos[s] = the move number of square s, from 0 to n*n-1, as an integer column tied to the
  // binaries by an equality row
  std::vector<dcp::Lin> pos(squares);
  for (int s = 0; s < squares; ++s) {
    pos[s] = dcp::new_var(h, 0, squares - 1);
    dcp::Lin link = pos[s];
    for (int k = 0; k < squares; ++k)
      if (exists[s][k]) link = link - (double)k * on[s][k];
    dcp::add_row(h, link, 0, 0);
  }

  // x[i][j] = the move number of square (i, j)
  std::vector<std::vector<dcp::Lin>> x(n, std::vector<dcp::Lin>(n));
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; ++j) x[i][j] = pos[i * n + j];
  out.add("x", x);
}
