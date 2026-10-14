// Kakuro: fill the white cells with digits 1..9 so that each run of cells sums to its clue and contains no repeated digit.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int n = instance.at("n");
  const json& segments = instance.at("problem");

  // cell[r][c] is the digit in the white cell at row r, column c (1-based coordinates from the instance; index 0 unused).
  // Cells that belong to no clue run are black and stay null; they are output as 0.
  std::vector<std::vector<IntVar*>> cell(n + 1, std::vector<IntVar*>(n + 1, nullptr));

  // each clue is [sum, [r1, c1], [r2, c2], ...]: the white cells of one run add up to the clue and hold different digits
  for (const auto& seg : segments) {
    int clue = seg[0].get<int>();
    vec<IntVar*> run;
    vec<int> ones;
    for (size_t k = 1; k < seg.size(); ++k) {
      int r = seg[k][0].get<int>();
      int c = seg[k][1].get<int>();
      // a white cell holds a digit from 1 to 9
      if (cell[r][c] == nullptr) createVar(cell[r][c], 1, 9);
      run.push(cell[r][c]);
      ones.push(1);
    }
    // the digits of the run add up to the clue
    int_linear(ones, run, IRT_EQ, clue);
    // no digit is repeated within the run
    all_different(run);
  }

  // search on the white cells in reading order
  vec<IntVar*> flat;
  for (int r = 1; r <= n; ++r) {
    for (int c = 1; c <= n; ++c) {
      if (cell[r][c] != nullptr) flat.push(cell[r][c]);
    }
  }
  branch(flat, VAR_SIZE_MIN, VAL_MIN);

  // black cells are output as 0
  json grid = json::array();
  for (int r = 1; r <= n; ++r) {
    json row = json::array();
    for (int c = 1; c <= n; ++c) {
      IntVar* v = cell[r][c] != nullptr ? cell[r][c] : getConstant(0);
      row.push_back(dcp::out(v));
    }
    grid.push_back(row);
  }
  outputs = {{"x", grid}};
}
