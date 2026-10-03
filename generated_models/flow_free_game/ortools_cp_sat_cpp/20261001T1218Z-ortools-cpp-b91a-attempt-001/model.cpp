#include <cstdlib>
#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Flow Free: connect the matching coloured endpoints on the board with pipes
// that neither cross nor overlap, covering every cell. Each cell gets a colour;
// an endpoint has exactly one neighbour of its colour and every other cell has
// exactly two, so the cells of one colour form a path between its endpoints.
void Build(const json& instance, CpModelBuilder& model, json& outputs) {
  const auto board = instance.at("board").get<std::vector<std::vector<int>>>();
  const int M = static_cast<int>(board.size());
  const int N = static_cast<int>(board[0].size());

  // Colours range over 1..10, the domain the statement's model declares.
  std::vector<std::vector<IntVar>> B(M);
  for (int i = 0; i < M; ++i)
    for (int j = 0; j < N; ++j) B[i].push_back(model.NewIntVar(Domain(1, 10)));

  // same[a][b]: orthogonal neighbours a and b have the same colour. Each edge
  // is reified once in both directions and shared by its two cells.
  auto id = [N](int i, int j) { return i * N + j; };
  std::vector<std::vector<int>> slot(M * N, std::vector<int>(M * N, -1));
  std::vector<BoolVar> same;
  auto edge = [&](int i, int j, int k, int l) -> BoolVar {
    int& s = slot[id(i, j)][id(k, l)];
    if (s < 0) {
      const BoolVar b = model.NewBoolVar();
      model.AddEquality(B[i][j], B[k][l]).OnlyEnforceIf(b);
      model.AddNotEqual(B[i][j], B[k][l]).OnlyEnforceIf(b.Not());
      s = static_cast<int>(same.size());
      slot[id(k, l)][id(i, j)] = s;
      same.push_back(b);
    }
    return same[s];
  };

  for (int i = 0; i < M; ++i) {
    for (int j = 0; j < N; ++j) {
      // Number of orthogonal neighbours sharing this cell's colour.
      LinearExpr same_neighbours;
      for (int k = 0; k < M; ++k)
        for (int l = 0; l < N; ++l)
          if (std::abs(k - i) + std::abs(l - j) == 1) same_neighbours += edge(i, j, k, l);

      if (board[i][j] != 0) {
        // A given endpoint keeps its colour and has exactly one neighbour of
        // that colour: the pipe leaves it once.
        model.AddEquality(B[i][j], board[i][j]);
        model.AddEquality(same_neighbours, 1);
      } else {
        // An empty cell is filled by a pipe passing through it: exactly two
        // neighbours share its colour. (The statement's alternative "colour 0"
        // is outside the 1..10 domain and cannot hold.)
        model.AddEquality(same_neighbours, 2);
      }
    }
  }

  json leaves = json::array();
  for (int i = 0; i < M; ++i) {
    json row = json::array();
    for (int j = 0; j < N; ++j) row.push_back(B[i][j].index());
    leaves.push_back(row);
  }
  outputs = {{"B", leaves}};
}
