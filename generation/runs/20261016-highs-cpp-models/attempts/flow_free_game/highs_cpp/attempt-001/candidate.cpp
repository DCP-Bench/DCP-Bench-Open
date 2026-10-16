// Flow Free: connect the two cells of each colour with one pipe, so that the pipes
// cover the whole board, do not cross, and do not overlap. Output B is the colour
// of each cell (1-based colours).
#include <algorithm>
#include <vector>

#include "dcp.h"

namespace {
const int kDr[4] = {-1, 1, 0, 0};
const int kDc[4] = {0, 0, -1, 1};
const int kOpp[4] = {1, 0, 3, 2};
}  // namespace

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  std::vector<std::vector<int>> board = instance.at("board").get<std::vector<std::vector<int>>>();
  const int R = static_cast<int>(board.size());
  const int C = static_cast<int>(board[0].size());
  const int N = R * C;
  int K = 0;  // number of colours: the largest number on the board
  for (const auto& row : board)
    for (int v : row) K = std::max(K, v);

  auto cell = [C](int r, int c) { return r * C + c; };
  auto neighbour = [&](int a, int d) -> int {
    int r = a / C + kDr[d], c = a % C + kDc[d];
    if (r < 0 || r >= R || c < 0 || c >= C) return -1;
    return cell(r, c);
  };

  // X[a][k-1] = 1 if cell a carries colour k.
  std::vector<std::vector<dcp::Lin>> X(N, std::vector<dcp::Lin>(K));
  for (int a = 0; a < N; ++a)
    for (int k = 0; k < K; ++k) X[a][k] = dcp::new_var(h, 0, 1);

  // G[(a*4+d)*K + k-1] = 1 if the pipe of colour k runs from cell a to its neighbour in direction d.
  // F is the flow that carries the pipe's cells away from the first endpoint of each colour.
  auto arc = [K](int a, int d, int k) { return (a * 4 + d) * K + (k - 1); };
  std::vector<dcp::Lin> G(N * 4 * K), F(N * 4 * K);
  for (int a = 0; a < N; ++a)
    for (int d = 0; d < 4; ++d)
      if (neighbour(a, d) >= 0)
        for (int k = 1; k <= K; ++k) {
          G[arc(a, d, k)] = dcp::new_var(h, 0, 1);
          F[arc(a, d, k)] = dcp::new_var(h, 0, N, false);
        }

  // Each cell carries exactly one colour.
  for (int a = 0; a < N; ++a) {
    dcp::Lin one;
    for (int k = 0; k < K; ++k) one = one + X[a][k];
    dcp::add_row(h, one, 1, 1);
  }

  // The numbers on the board are fixed: a numbered cell has its own colour and no other.
  std::vector<int> given(N, 0);
  for (int r = 0; r < R; ++r)
    for (int c = 0; c < C; ++c) given[cell(r, c)] = board[r][c];
  for (int a = 0; a < N; ++a)
    if (given[a] != 0)
      for (int k = 1; k <= K; ++k) dcp::add_row(h, X[a][k - 1], k == given[a] ? 1 : 0, k == given[a] ? 1 : 0);

  // The first cell of each colour is the source of its flow.
  std::vector<int> source(K + 1, -1);
  for (int a = 0; a < N; ++a)
    if (given[a] != 0 && source[given[a]] < 0) source[given[a]] = a;

  // An arc needs both its cells in its colour, and two opposite arcs cannot both be used.
  for (int a = 0; a < N; ++a)
    for (int d = 0; d < 4; ++d) {
      int b = neighbour(a, d);
      if (b < 0) continue;
      for (int k = 1; k <= K; ++k) {
        // a pipe moves only between two cells of its own colour
        dcp::add_row(h, G[arc(a, d, k)] - X[a][k - 1], -kHighsInf, 0);
        dcp::add_row(h, G[arc(a, d, k)] - X[b][k - 1], -kHighsInf, 0);
        // the flow goes only along an arc in use
        dcp::add_row(h, F[arc(a, d, k)] - double(N) * G[arc(a, d, k)], -kHighsInf, 0);
        // the two directions of one edge are not both used
        if (d == 1 || d == 3)
          dcp::add_row(h, G[arc(a, d, k)] + G[arc(b, kOpp[d], k)], -kHighsInf, 1);
      }
    }

  // Pipe shape: each numbered cell is the end of one pipe segment, and every other
  // cell of a colour has two pipe neighbours (in and out of the pipe).
  for (int a = 0; a < N; ++a)
    for (int k = 1; k <= K; ++k) {
      dcp::Lin degree;
      for (int d = 0; d < 4; ++d) {
        int b = neighbour(a, d);
        if (b < 0) continue;
        degree = degree + G[arc(a, d, k)] + G[arc(b, kOpp[d], k)];
      }
      if (given[a] == k)
        dcp::add_row(h, degree, 1, 1);
      else
        dcp::add_row(h, degree - 2.0 * X[a][k - 1], 0, 0);
    }

  // Connectivity: the flow starts at the first endpoint of a colour with one unit per
  // cell of that colour and every cell uses one unit. A loop with no endpoint cannot
  // get flow, so every pipe is one path from its endpoint.
  for (int k = 1; k <= K; ++k) {
    dcp::Lin total;
    for (int a = 0; a < N; ++a) total = total + X[a][k - 1];
    for (int a = 0; a < N; ++a) {
      dcp::Lin net = X[a][k - 1];
      for (int d = 0; d < 4; ++d) {
        int b = neighbour(a, d);
        if (b < 0) continue;
        net = net + F[arc(a, d, k)] - F[arc(b, kOpp[d], k)];
      }
      if (source[k] == a) net = net - total;
      dcp::add_row(h, net, 0, 0);
    }
  }

  // Output: the colour of each cell.
  std::vector<std::vector<dcp::Lin>> B(R, std::vector<dcp::Lin>(C));
  for (int r = 0; r < R; ++r)
    for (int c = 0; c < C; ++c) {
      dcp::Lin colour;
      for (int k = 1; k <= K; ++k) colour = colour + double(k) * X[cell(r, c)][k - 1];
      B[r][c] = colour;
    }
  out.add("B", B);
}
