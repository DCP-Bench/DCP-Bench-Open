#include <map>
#include <utility>
#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Solitaire battleships: fill a grid so that every cell is water, a one-cell
// submarine or a piece of a longer ship (left/right/top/bottom end or middle),
// the ships match the fleet, no two ships touch (not even at a corner), and
// the number of ship cells in every row and column matches the clues.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int rows = instance.at("rows").get<int>();
  const int cols = instance.at("cols").get<int>();
  const std::vector<int64_t> rowsum =
      instance.at("rowsum").get<std::vector<int64_t>>();
  const std::vector<int64_t> colsum =
      instance.at("colsum").get<std::vector<int64_t>>();
  // fleet[size] = number of ships of that size.
  std::map<int64_t, int64_t> fleet;
  for (const json& entry : instance.at("fleet_counts")) {
    fleet[entry.at(0).get<int64_t>()] = entry.at(1).get<int64_t>();
  }
  // The cell codes the instance uses: water, submarine (CIRCLE) and the five
  // ship pieces.  (The instance also lists _SHIP = 1, a generic ship cell; as in
  // the reference, no rule singles it out, so it is just one of the values.)
  const int WATER = instance.at("WATER").get<int>();
  const int CIRCLE = instance.at("CIRCLE").get<int>();
  const int LEFT = instance.at("LEFT").get<int>();
  const int RIGHT = instance.at("RIGHT").get<int>();
  const int TOP = instance.at("TOP").get<int>();
  const int BOTTOM = instance.at("BOTTOM").get<int>();
  const int MIDDLE = instance.at("MIDDLE").get<int>();
  // Initial shots: [row, col, cell code].
  const json& hints = instance.at("hints");

  // Cell codes run from 0 to 7, the domain the reference declares.
  const int kCodes = 8;

  // grid[r][c] is the code of cell (r, c).  is_code[r][c][v] is true exactly
  // when the cell holds code v; it is the one-hot form of grid[r][c], which lets
  // the neighbour rules below be stated as clauses over booleans.
  std::vector<std::vector<IntVar>> grid(rows);
  std::vector<std::vector<std::vector<BoolVar>>> is_code(
      rows, std::vector<std::vector<BoolVar>>(cols));
  for (int r = 0; r < rows; ++r) {
    for (int c = 0; c < cols; ++c) {
      grid[r].push_back(model.NewIntVar(Domain(0, kCodes - 1)));
      LinearExpr one_code;
      LinearExpr code_value;
      for (int v = 0; v < kCodes; ++v) {
        is_code[r][c].push_back(model.NewBoolVar());
        one_code += is_code[r][c][v];
        code_value += v * is_code[r][c][v];
      }
      model.AddEquality(one_code, 1);
      model.AddEquality(grid[r][c], code_value);
    }
  }

  // --- Helpers that name boolean conditions on cells. ---

  // A literal that is true exactly when cell (r, c) holds one of the codes.
  auto cell_in = [&](int r, int c, const std::vector<int>& codes) -> BoolVar {
    if (codes.size() == 1) return is_code[r][c][codes[0]];
    BoolVar any = model.NewBoolVar();
    std::vector<BoolVar> options, none;
    for (const int v : codes) {
      options.push_back(is_code[r][c][v]);
      none.push_back(is_code[r][c][v].Not());
    }
    model.AddBoolOr(options).OnlyEnforceIf(any);
    model.AddBoolAnd(none).OnlyEnforceIf(any.Not());
    return any;
  };
  // A literal that is true exactly when all the given literals are true.
  auto all_of = [&](const std::vector<BoolVar>& lits) -> BoolVar {
    BoolVar all = model.NewBoolVar();
    model.AddBoolAnd(lits).OnlyEnforceIf(all);
    std::vector<BoolVar> some_false;
    for (const BoolVar& l : lits) some_false.push_back(l.Not());
    some_false.push_back(all);
    model.AddBoolOr(some_false);
    return all;
  };
  auto inside = [&](int r, int c) {
    return r >= 0 && r < rows && c >= 0 && c < cols;
  };

  // --- Hints. ---
  // Each initial shot fixes one cell to the given code.
  for (const json& hint : hints) {
    const int r = hint.at(0).get<int>();
    const int c = hint.at(1).get<int>();
    const int v = hint.at(2).get<int>();
    model.AddEquality(grid[r][c], v);
  }

  // --- Row and column sums. ---
  // occupied[r][c] is true when the cell holds anything other than water; every
  // such cell counts as a ship segment.
  std::vector<std::vector<BoolVar>> occupied(rows);
  for (int r = 0; r < rows; ++r) {
    for (int c = 0; c < cols; ++c) {
      occupied[r].push_back(model.NewBoolVar());
      LinearExpr above_water;
      for (int v = WATER + 1; v < kCodes; ++v) above_water += is_code[r][c][v];
      model.AddEquality(occupied[r][c], above_water);
    }
  }
  // The number of ship cells in each row matches its clue.
  for (int r = 0; r < rows; ++r) {
    LinearExpr in_row;
    for (int c = 0; c < cols; ++c) in_row += occupied[r][c];
    model.AddEquality(in_row, rowsum[r]);
  }
  // The number of ship cells in each column matches its clue.
  for (int c = 0; c < cols; ++c) {
    LinearExpr in_column;
    for (int r = 0; r < rows; ++r) in_column += occupied[r][c];
    model.AddEquality(in_column, colsum[c]);
  }

  // --- Adjacency and connectivity. ---
  const std::vector<std::pair<int, int>> diagonals = {
      {-1, -1}, {-1, 1}, {1, -1}, {1, 1}};
  const std::vector<std::pair<int, int>> orthogonals = {
      {-1, 0}, {1, 0}, {0, -1}, {0, 1}};

  // An end piece (left, right, top or bottom) continues into one neighbour
  // (main_step) holding one of main_codes, and every other orthogonal neighbour
  // that exists is water.  A piece whose continuing neighbour is off the grid
  // cannot be placed there.
  auto end_piece = [&](int r, int c, int piece, std::pair<int, int> main_step,
                       const std::vector<int>& main_codes) {
    const BoolVar here = is_code[r][c][piece];
    std::vector<BoolVar> required;
    if (!inside(r + main_step.first, c + main_step.second)) {
      model.AddBoolAnd({here.Not()});
      return;
    }
    required.push_back(
        cell_in(r + main_step.first, c + main_step.second, main_codes));
    for (const auto& step : orthogonals) {
      if (step == main_step) continue;
      // The three other sides of an end piece are water.
      if (inside(r + step.first, c + step.second)) {
        required.push_back(is_code[r + step.first][c + step.second][WATER]);
      }
    }
    model.AddBoolAnd(required).OnlyEnforceIf(here);
  };

  for (int r = 0; r < rows; ++r) {
    for (int c = 0; c < cols; ++c) {
      // No diagonal (corner) contact: a ship cell has water on its diagonals.
      for (const auto& step : diagonals) {
        if (inside(r + step.first, c + step.second)) {
          model.AddImplication(occupied[r][c],
                               is_code[r + step.first][c + step.second][WATER]);
        }
      }

      // A submarine is surrounded by water on all four sides.
      for (const auto& step : orthogonals) {
        if (inside(r + step.first, c + step.second)) {
          model.AddImplication(is_code[r][c][CIRCLE],
                               is_code[r + step.first][c + step.second][WATER]);
        }
      }

      // A left end is followed on its right by a middle or the right end, with
      // water on its other sides.
      end_piece(r, c, LEFT, {0, 1}, {MIDDLE, RIGHT});
      // A right end follows a middle or the left end on its left.
      end_piece(r, c, RIGHT, {0, -1}, {MIDDLE, LEFT});
      // A top end is followed below by a middle or the bottom end.
      end_piece(r, c, TOP, {1, 0}, {MIDDLE, BOTTOM});
      // A bottom end follows a middle or the top end above it.
      end_piece(r, c, BOTTOM, {-1, 0}, {MIDDLE, TOP});

      // A middle piece lies either in a horizontal ship (left/middle before it,
      // right/middle after it, water above and below) or in a vertical ship
      // (top/middle above it, bottom/middle below it, water left and right).
      std::vector<BoolVar> shapes;
      if (c > 0 && c < cols - 1) {
        std::vector<BoolVar> horizontal = {
            cell_in(r, c - 1, {LEFT, MIDDLE}),
            cell_in(r, c + 1, {RIGHT, MIDDLE})};
        if (r > 0) horizontal.push_back(is_code[r - 1][c][WATER]);
        if (r < rows - 1) horizontal.push_back(is_code[r + 1][c][WATER]);
        shapes.push_back(all_of(horizontal));
      }
      if (r > 0 && r < rows - 1) {
        std::vector<BoolVar> vertical = {
            cell_in(r - 1, c, {TOP, MIDDLE}),
            cell_in(r + 1, c, {BOTTOM, MIDDLE})};
        if (c > 0) vertical.push_back(is_code[r][c - 1][WATER]);
        if (c < cols - 1) vertical.push_back(is_code[r][c + 1][WATER]);
        shapes.push_back(all_of(vertical));
      }
      if (shapes.empty()) {
        model.AddBoolAnd({is_code[r][c][MIDDLE].Not()});
      } else {
        model.AddBoolOr(shapes).OnlyEnforceIf(is_code[r][c][MIDDLE]);
      }
    }
  }

  // --- Fleet composition. ---
  // Submarines (size 1): exactly the listed number of CIRCLE cells.
  LinearExpr submarines;
  for (int r = 0; r < rows; ++r) {
    for (int c = 0; c < cols; ++c) submarines += is_code[r][c][CIRCLE];
  }
  model.AddEquality(submarines, fleet.at(1));

  // Longer ships, counted by size: a ship of the given size is an end piece,
  // size - 2 middle pieces and the other end piece in one line.  The
  // connectivity rules above make every run of ship pieces one such ship.
  int64_t longer_ships = 0;
  for (const auto& [size, count] : fleet) {
    if (size < 2) continue;
    longer_ships += count;
    std::vector<BoolVar> placements;
    for (int r = 0; r < rows; ++r) {
      for (int c = 0; c + size <= cols; ++c) {
        std::vector<BoolVar> parts = {is_code[r][c][LEFT],
                                      is_code[r][c + size - 1][RIGHT]};
        for (int k = 1; k < size - 1; ++k) parts.push_back(is_code[r][c + k][MIDDLE]);
        placements.push_back(all_of(parts));
      }
    }
    for (int r = 0; r + size <= rows; ++r) {
      for (int c = 0; c < cols; ++c) {
        std::vector<BoolVar> parts = {is_code[r][c][TOP],
                                      is_code[r + size - 1][c][BOTTOM]};
        for (int k = 1; k < size - 1; ++k) parts.push_back(is_code[r + k][c][MIDDLE]);
        placements.push_back(all_of(parts));
      }
    }
    LinearExpr ships_of_size;
    for (const BoolVar& p : placements) ships_of_size += p;
    model.AddEquality(ships_of_size, count);
  }

  // No ship of a size the fleet does not list: every left or top end starts one
  // of the ships counted above, so there are exactly as many of them as ships.
  LinearExpr starts;
  for (int r = 0; r < rows; ++r) {
    for (int c = 0; c < cols; ++c) {
      starts += is_code[r][c][LEFT];
      starts += is_code[r][c][TOP];
    }
  }
  model.AddEquality(starts, longer_ships);

  json grid_out = json::array();
  for (int r = 0; r < rows; ++r) {
    json row = json::array();
    for (int c = 0; c < cols; ++c) row.push_back(grid[r][c].index());
    grid_out.push_back(row);
  }
  outputs = {{"grid", grid_out}};
}
