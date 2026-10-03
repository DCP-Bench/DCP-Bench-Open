#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// N-puzzle (sliding tiles): on a dim x dim board with one empty tile (0), slide
// tiles into the empty place, one move per step, to get from the start board
// to the end board in exactly N_STEPS boards (start and end included). The
// board must change at every step.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int n_steps = instance.at("N_STEPS").get<int>();
  const std::vector<std::vector<int64_t>> puzzle_start =
      instance.at("puzzle_start").get<std::vector<std::vector<int64_t>>>();
  const std::vector<std::vector<int64_t>> puzzle_end =
      instance.at("puzzle_end").get<std::vector<std::vector<int64_t>>>();
  const int dim = static_cast<int>(puzzle_start.size());
  const int n = dim * dim - 1;  // tiles are numbered 1..n and 0 is the empty tile

  // x[t][i][j] is the tile at row i, column j at step t.
  std::vector<std::vector<std::vector<IntVar>>> x(n_steps);
  for (int t = 0; t < n_steps; ++t) {
    x[t].resize(dim);
    for (int i = 0; i < dim; ++i)
      for (int j = 0; j < dim; ++j) x[t][i].push_back(model.NewIntVar(Domain(0, n)));
  }

  // The first board is the start state and the last board is the end state.
  for (int i = 0; i < dim; ++i) {
    for (int j = 0; j < dim; ++j) {
      model.AddEquality(x[0][i][j], puzzle_start[i][j]);
      model.AddEquality(x[n_steps - 1][i][j], puzzle_end[i][j]);
    }
  }

  // is_empty[t][i][j] is true exactly when the empty tile is at (i, j) at step t.
  // It is used both positively and negatively below, so both directions are posted.
  std::vector<std::vector<std::vector<BoolVar>>> is_empty(n_steps);
  for (int t = 0; t < n_steps; ++t) {
    is_empty[t].resize(dim);
    for (int i = 0; i < dim; ++i) {
      for (int j = 0; j < dim; ++j) {
        const BoolVar b = model.NewBoolVar();
        model.AddEquality(x[t][i][j], 0).OnlyEnforceIf(b);
        model.AddNotEqual(x[t][i][j], 0).OnlyEnforceIf(b.Not());
        is_empty[t][i].push_back(b);
      }
    }
  }

  // Each step is one move from the previous board to the next one.
  for (int t = 1; t < n_steps; ++t) {
    // In every step all tiles (and the empty tile) are different.
    std::vector<IntVar> board;
    for (int i = 0; i < dim; ++i)
      for (int j = 0; j < dim; ++j) board.push_back(x[t][i][j]);
    model.AddAllDifferent(board);

    std::vector<BoolVar> differs;  // cells whose tile changes in this step
    for (int i = 0; i < dim; ++i) {
      for (int j = 0; j < dim; ++j) {
        // The empty tile can only be at (i, j) after the step if it was at
        // (i, j) or at one of the cells directly above, below, left or right.
        std::vector<BoolVar> was_empty_nearby;
        const int moves[5][2] = {{0, 0}, {-1, 0}, {1, 0}, {0, -1}, {0, 1}};
        for (const auto& m : moves) {
          const int r = i + m[0], c = j + m[1];
          if (r >= 0 && r < dim && c >= 0 && c < dim) was_empty_nearby.push_back(is_empty[t - 1][r][c]);
        }
        was_empty_nearby.push_back(is_empty[t][i][j].Not());  // or (i, j) is not empty after the step
        model.AddBoolOr(was_empty_nearby);

        // Only the empty tile moves: a cell keeps its tile unless the empty
        // tile was there before or is there after.
        const BoolVar same = model.NewBoolVar();
        model.AddEquality(x[t - 1][i][j], x[t][i][j]).OnlyEnforceIf(same);
        model.AddBoolOr({is_empty[t - 1][i][j], is_empty[t][i][j], same});

        // Collect "this cell changed" for the no-freezing rule below.
        const BoolVar changed = model.NewBoolVar();
        model.AddNotEqual(x[t - 1][i][j], x[t][i][j]).OnlyEnforceIf(changed);
        differs.push_back(changed);
      }
    }
    // The board must change between consecutive steps (no freezing).
    model.AddBoolOr(differs);
  }

  json out = json::array();
  for (int t = 0; t < n_steps; ++t) {
    json board = json::array();
    for (int i = 0; i < dim; ++i) {
      json row = json::array();
      for (int j = 0; j < dim; ++j) row.push_back(x[t][i][j].index());
      board.push_back(row);
    }
    out.push_back(board);
  }
  outputs = {{"steps", out}};
}
