// Sudoku: fill a 9x9 grid with digits so that each row, each column and each
// 3x3 section contains the digits 1 to 9 once. The clues in input_grid are kept
// (0 means an empty cell). Output: grid, the solved 9x9 grid.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const int N = 9;
  const auto& clues = instance.at("input_grid");

  // x[i][j] is the digit in cell (i, j). y[i][j][v] is 1 when cell (i, j) holds digit v+1.
  std::vector<std::vector<dcp::Lin>> x(N, std::vector<dcp::Lin>(N));
  std::vector<std::vector<std::vector<dcp::Lin>>> y(
      N, std::vector<std::vector<dcp::Lin>>(N, std::vector<dcp::Lin>(N)));

  // Each cell holds exactly one digit.
  for (int i = 0; i < N; i++) {
    for (int j = 0; j < N; j++) {
      int clue = clues[i][j].get<int>();
      // A clue fixes the cell's digit; an empty cell takes any digit from 1 to 9.
      if (clue > 0) {
        x[i][j] = dcp::new_var(h, clue, clue);
      } else {
        x[i][j] = dcp::new_var(h, 1, N);
      }
      dcp::Lin one_hot;
      for (int v = 0; v < N; v++) {
        y[i][j][v] = dcp::new_var(h, 0, 1);
        one_hot = one_hot + y[i][j][v];
      }
      // // each cell holds exactly one digit
      dcp::add_row(h, one_hot, 1, 1);
      // // the cell's digit is the digit whose indicator is 1
      dcp::Lin digit;
      for (int v = 0; v < N; v++) digit = digit + (double)(v + 1) * y[i][j][v];
      dcp::add_row(h, x[i][j] - digit, 0, 0);
    }
  }

  // // each row contains every digit once
  for (int i = 0; i < N; i++) {
    for (int v = 0; v < N; v++) {
      dcp::Lin count;
      for (int j = 0; j < N; j++) count = count + y[i][j][v];
      dcp::add_row(h, count, 1, 1);
    }
  }

  // // each column contains every digit once
  for (int j = 0; j < N; j++) {
    for (int v = 0; v < N; v++) {
      dcp::Lin count;
      for (int i = 0; i < N; i++) count = count + y[i][j][v];
      dcp::add_row(h, count, 1, 1);
    }
  }

  // // each 3x3 section contains every digit once
  for (int bi = 0; bi < 3; bi++) {
    for (int bj = 0; bj < 3; bj++) {
      for (int v = 0; v < N; v++) {
        dcp::Lin count;
        for (int di = 0; di < 3; di++) {
          for (int dj = 0; dj < 3; dj++) {
            count = count + y[3 * bi + di][3 * bj + dj][v];
          }
        }
        dcp::add_row(h, count, 1, 1);
      }
    }
  }

  out.add("grid", x);
}
