// Solitaire Battleships: place a fleet on a grid so that no two ships touch (even diagonally),
// row and column sums are met and the given shots are respected.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int rows = instance.at("rows");
  int cols = instance.at("cols");
  std::vector<int> rowsum = instance.at("rowsum").get<std::vector<int>>();
  std::vector<int> colsum = instance.at("colsum").get<std::vector<int>>();
  std::vector<std::vector<int>> fleet = instance.at("fleet_counts").get<std::vector<std::vector<int>>>();
  std::vector<std::vector<int>> hints = instance.at("hints").get<std::vector<std::vector<int>>>();
  int WATER = instance.at("WATER"), SHIP = instance.at("_SHIP"), CIRCLE = instance.at("CIRCLE");
  int LEFT = instance.at("LEFT"), RIGHT = instance.at("RIGHT"), TOP = instance.at("TOP");
  int BOTTOM = instance.at("BOTTOM"), MIDDLE = instance.at("MIDDLE");

  // grid[r][c] is water, a submarine (CIRCLE) or a ship part (LEFT, RIGHT, TOP, BOTTOM, MIDDLE);
  // the generic _SHIP code is not used in a solution because every part is told apart
  vec<vec<IntVar*>> grid;
  createVars(grid, rows, cols, 0, 7, true);
  for (int r = 0; r < rows; ++r)
    for (int c = 0; c < cols; ++c) int_rel(grid[r][c], IRT_NE, SHIP);

  // cell(r, c) is the cell, with water outside the grid (a constant)
  auto cell = [&](int r, int c) -> IntVar* {
    if (r < 0 || r >= rows || c < 0 || c >= cols) return getConstant(WATER);
    return grid[r][c];
  };

  // the shots taken to start you off: the shown cell has the given content
  for (auto& h : hints) int_rel(grid[h[0]][h[1]], IRT_EQ, h[2]);

  // ships are straight: a ship part is joined to its neighbours as its type demands, and every other orthogonal
  // neighbour is water. Water cells have no condition of their own, the neighbouring ship parts constrain them.
  int vals[7] = {WATER, CIRCLE, LEFT, RIGHT, TOP, BOTTOM, MIDDLE};
  auto is_in = [&](int v, std::vector<int> set) {
    for (int s : set)
      if (s == v) return true;
    return false;
  };
  vec<vec<int>> local;  // tuples (cell, north, south, east, west)
  for (int v : vals)
    for (int nn : vals)
      for (int ss : vals)
        for (int ee : vals)
          for (int ww : vals) {
            bool ok;
            if (v == WATER) {
              ok = true;
            } else if (v == CIRCLE) {
              ok = nn == WATER && ss == WATER && ee == WATER && ww == WATER;
            } else if (v == LEFT) {
              ok = nn == WATER && ss == WATER && ww == WATER && is_in(ee, {RIGHT, MIDDLE});
            } else if (v == RIGHT) {
              ok = nn == WATER && ss == WATER && ee == WATER && is_in(ww, {LEFT, MIDDLE});
            } else if (v == TOP) {
              ok = ww == WATER && ee == WATER && nn == WATER && is_in(ss, {BOTTOM, MIDDLE});
            } else if (v == BOTTOM) {
              ok = ww == WATER && ee == WATER && ss == WATER && is_in(nn, {TOP, MIDDLE});
            } else {  // MIDDLE of a horizontal or of a vertical ship
              bool horizontal = nn == WATER && ss == WATER && is_in(ww, {LEFT, MIDDLE}) && is_in(ee, {RIGHT, MIDDLE});
              bool vertical = ww == WATER && ee == WATER && is_in(nn, {TOP, MIDDLE}) && is_in(ss, {BOTTOM, MIDDLE});
              ok = horizontal || vertical;
            }
            if (ok) {
              local.push();
              local.last().push(v);
              local.last().push(nn);
              local.last().push(ss);
              local.last().push(ee);
              local.last().push(ww);
            }
          }
  for (int r = 0; r < rows; ++r)
    for (int c = 0; c < cols; ++c) {
      vec<IntVar*> around;
      around.push(grid[r][c]);
      around.push(cell(r - 1, c));
      around.push(cell(r + 1, c));
      around.push(cell(r, c + 1));
      around.push(cell(r, c - 1));
      table(around, local);
    }

  // no two ships occupy adjacent grid squares, not even diagonally: of two diagonal neighbours one is water
  vec<vec<int>> not_both;
  for (int a : vals)
    for (int b : vals)
      if (a == WATER || b == WATER) {
        not_both.push();
        not_both.last().push(a);
        not_both.last().push(b);
      }
  for (int r = 0; r + 1 < rows; ++r)
    for (int c = 0; c < cols; ++c)
      for (int dc = -1; dc <= 1; dc += 2) {
        if (c + dc < 0 || c + dc >= cols) continue;
        vec<IntVar*> diag;
        diag.push(grid[r][c]);
        diag.push(grid[r + 1][c + dc]);
        table(diag, not_both);
      }

  // occupied[r][c] is true when the cell holds part of a vessel
  vec<vec<BoolView>> occupied;
  createVars(occupied, rows, cols);
  for (int r = 0; r < rows; ++r)
    for (int c = 0; c < cols; ++c) int_rel_reif(grid[r][c], IRT_NE, WATER, occupied[r][c]);

  // the digits next to the grid give the number of occupied squares in each row
  for (int r = 0; r < rows; ++r) {
    vec<BoolView> line;
    for (int c = 0; c < cols; ++c) line.push(occupied[r][c]);
    bool_linear(line, IRT_EQ, getConstant(rowsum[r]));
  }

  // the digits below the grid give the number of occupied squares in each column
  for (int c = 0; c < cols; ++c) {
    vec<BoolView> line;
    for (int r = 0; r < rows; ++r) line.push(occupied[r][c]);
    bool_linear(line, IRT_EQ, getConstant(colsum[c]));
  }

  // the fleet: fleet_counts lists (length, how many) ships. A ship of length 1 is a submarine; a longer ship
  // starts with LEFT or TOP, continues with MIDDLE parts and ends with RIGHT or BOTTOM.
  for (auto& f : fleet) {
    int len = f[0], count = f[1];
    vec<BoolView> starts;
    if (len == 1) {
      for (int r = 0; r < rows; ++r)
        for (int c = 0; c < cols; ++c) {
          BoolView b = newBoolVar();
          int_rel_reif(grid[r][c], IRT_EQ, CIRCLE, b);
          starts.push(b);
        }
    } else {
      for (int r = 0; r < rows; ++r)
        for (int c = 0; c < cols; ++c)
          for (int dir = 0; dir < 2; ++dir) {  // 0 horizontal, 1 vertical
            int er = r + (dir ? len - 1 : 0), ec = c + (dir ? 0 : len - 1);
            if (er >= rows || ec >= cols) continue;
            vec<BoolView> parts;
            for (int k = 0; k < len; ++k) {
              int code = k == 0 ? (dir ? TOP : LEFT) : (k == len - 1 ? (dir ? BOTTOM : RIGHT) : MIDDLE);
              BoolView p = newBoolVar();
              int_rel_reif(grid[r + (dir ? k : 0)][c + (dir ? 0 : k)], IRT_EQ, code, p);
              parts.push(p);
            }
            BoolView whole = newBoolVar();
            array_bool_and(parts, whole);
            starts.push(whole);
          }
    }
    bool_linear(starts, IRT_EQ, getConstant(count));
  }

  vec<IntVar*> flat;
  flatten(grid, flat);
  branch(flat, VAR_INORDER, VAL_MIN);
  json out = json::array();
  for (int r = 0; r < rows; ++r) {
    json row = json::array();
    for (int c = 0; c < cols; ++c) row.push_back(dcp::out(grid[r][c]));
    out.push_back(row);
  }
  outputs = {{"grid", out}};
}
