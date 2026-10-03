#include <algorithm>
#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Maximum density still life (CSPLib 32): find the most densely populated
// pattern of live cells on an n x m active grid that is stable under Conway's
// Game of Life. The board is infinite; cells outside the active grid are dead
// and must stay dead.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const int n = instance.at("n").get<int>();
  const int m = instance.at("m").get<int>();

  // grid[i][j] is true when cell (i, j) of the active grid is alive.
  std::vector<std::vector<BoolVar>> grid(n);
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < m; ++j) grid[i].push_back(model.NewBoolVar());

  // Still-life rules inside the active grid, counting live neighbours among
  // the up to eight surrounding cells that lie in the grid:
  // a live cell has exactly 2 or 3 live neighbours; a dead cell does not have
  // exactly 3 (otherwise it would be born).
  for (int i = 0; i < n; ++i) {
    for (int j = 0; j < m; ++j) {
      LinearExpr neighbours;
      for (int di = -1; di <= 1; ++di)
        for (int dj = -1; dj <= 1; ++dj) {
          if (di == 0 && dj == 0) continue;
          const int ni = i + di, nj = j + dj;
          if (0 <= ni && ni < n && 0 <= nj && nj < m) neighbours += grid[ni][nj];
        }
      model.AddLinearConstraint(neighbours, Domain(2, 3)).OnlyEnforceIf(grid[i][j]);
      model.AddNotEqual(neighbours, 3).OnlyEnforceIf(grid[i][j].Not());
    }
  }

  // Dead cells just outside the grid must not be born: the cell above row 0,
  // below row n-1, left of column 0 or right of column m-1 sees up to three
  // grid cells, and these must not be exactly 3 live ones.
  for (int j = 0; j < m; ++j) {
    LinearExpr top, bottom;
    for (int jj = std::max(0, j - 1); jj < std::min(m, j + 2); ++jj) {
      top += grid[0][jj];
      bottom += grid[n - 1][jj];
    }
    model.AddNotEqual(top, 3);
    model.AddNotEqual(bottom, 3);
  }
  for (int i = 0; i < n; ++i) {
    LinearExpr left, right;
    for (int ii = std::max(0, i - 1); ii < std::min(n, i + 2); ++ii) {
      left += grid[ii][0];
      right += grid[ii][m - 1];
    }
    model.AddNotEqual(left, 3);
    model.AddNotEqual(right, 3);
  }

  // Maximize the number of live cells in the active grid.
  LinearExpr live;
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < m; ++j) live += grid[i][j];
  model.Maximize(live);

  json out = json::array();
  for (int i = 0; i < n; ++i) {
    json row = json::array();
    for (int j = 0; j < m; ++j) row.push_back(grid[i][j].index());
    out.push_back(row);
  }
  outputs = {{"grid", out}};
}
