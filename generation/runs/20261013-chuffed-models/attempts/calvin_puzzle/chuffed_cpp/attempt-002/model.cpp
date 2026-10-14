// Calvin puzzle: fill an n x n grid with the numbers 1 to n^2 in one sequence, so that
// each number is placed relative to the previous one by one of two moves.
// Move I: vertically or horizontally, exactly three squares away (a two-square gap).
// Move II: diagonally, exactly two squares away (a one-square gap).
// The starting square is free. The grid is printed row by row.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int n = instance.at("n");
  int N = n * n;

  // cell[p] is the number written in square p (row-major), numbers 1..N
  vec<IntVar*> cell;
  createVars(cell, N, 1, N);
  // fill every square with a different number
  all_different(cell);

  // pos[k] is the square (0-based, row-major) holding the number k; the offset 1 is for the 1-based numbers
  vec<IntVar*> pos;
  createVars(pos, N, 0, N - 1);
  inverse(cell, pos, 1, 0);

  // the next number is placed by move I (three squares vertically or horizontally)
  // or move II (two squares diagonally). Allowed square pairs are listed as a table.
  int moves[8][2] = {{0, 3}, {0, -3}, {3, 0}, {-3, 0}, {2, 2}, {2, -2}, {-2, 2}, {-2, -2}};
  for (int k = 0; k + 1 < N; ++k) {
    vec<vec<int>> allowed;
    for (int r = 0; r < n; ++r) {
      for (int c = 0; c < n; ++c) {
        for (int m = 0; m < 8; ++m) {
          int nr = r + moves[m][0], nc = c + moves[m][1];
          if (nr < 0 || nr >= n || nc < 0 || nc >= n) continue;
          allowed.push();
          allowed.last().push(r * n + c);
          allowed.last().push(nr * n + nc);
        }
      }
    }
    vec<IntVar*> step;
    step.push(pos[k]);
    step.push(pos[k + 1]);
    table(step, allowed);
  }

  // branch on the squares in the order the numbers 1, 2, ... are visited
  branch(pos, VAR_INORDER, VAL_MIN);

  json rows = json::array();
  for (int r = 0; r < n; ++r) {
    json row = json::array();
    for (int c = 0; c < n; ++c) row.push_back(dcp::out(cell[r * n + c]));
    rows.push_back(row);
  }
  outputs = {{"x", rows}};
}
