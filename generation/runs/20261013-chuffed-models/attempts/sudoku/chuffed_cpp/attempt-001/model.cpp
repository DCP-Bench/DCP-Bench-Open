// Sudoku: fill a 9 x 9 grid with the digits 1 to 9 so that every row, every column and every
// 3 x 3 section contains each digit once, keeping the given clues.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  std::vector<std::vector<int>> clues = instance.at("input_grid").get<std::vector<std::vector<int>>>();

  // grid[i][j] is the digit in row i, column j
  vec<vec<IntVar*>> grid;
  createVars(grid, 9, 9, 1, 9);

  // the clues of the input are fixed (0 marks an empty cell)
  for (int i = 0; i < 9; ++i) {
    for (int j = 0; j < 9; ++j) {
      if (clues[i][j] != 0) int_rel(grid[i][j], IRT_EQ, clues[i][j]);
    }
  }

  // every row contains each digit once
  for (int i = 0; i < 9; ++i) {
    vec<IntVar*> row;
    for (int j = 0; j < 9; ++j) row.push(grid[i][j]);
    all_different(row);
  }

  // every column contains each digit once
  for (int j = 0; j < 9; ++j) {
    vec<IntVar*> col;
    for (int i = 0; i < 9; ++i) col.push(grid[i][j]);
    all_different(col);
  }

  // every 3 x 3 section contains each digit once
  for (int bi = 0; bi < 3; ++bi) {
    for (int bj = 0; bj < 3; ++bj) {
      vec<IntVar*> box;
      for (int i = 0; i < 3; ++i) {
        for (int j = 0; j < 3; ++j) box.push(grid[3 * bi + i][3 * bj + j]);
      }
      all_different(box);
    }
  }

  // decide the cells in reading order, trying the fewest-candidate cell first
  vec<IntVar*> cells;
  for (int i = 0; i < 9; ++i) {
    for (int j = 0; j < 9; ++j) cells.push(grid[i][j]);
  }
  branch(cells, VAR_SIZE_MIN, VAL_MIN);

  json rows = json::array();
  for (int i = 0; i < 9; ++i) {
    json row = json::array();
    for (int j = 0; j < 9; ++j) row.push_back(dcp::out(grid[i][j]));
    rows.push_back(row);
  }
  outputs = {{"grid", rows}};
}
