// Calvin puzzle: fill an n x n grid with the numbers 1 to n*n so that each number follows the previous one by a fixed move.
// A move is either exactly three squares along a row or a column, or exactly two squares diagonally.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int n = instance.at("n");
  int cells = n * n;

  // row[k] and col[k] are the row and column of the square holding the number k+1
  vec<IntVar*> row, col;
  createVars(row, cells, 0, n - 1);
  createVars(col, cells, 0, n - 1);

  // pos[k] is the square of the number k+1, numbered row by row from 0 to n*n-1
  vec<IntVar*> pos;
  createVars(pos, cells, 0, cells - 1);
  for (int k = 0; k < cells; ++k) {
    vec<IntVar*> rc;
    rc.push(row[k]); rc.push(col[k]);
    vec<int> coef;
    coef.push(n); coef.push(1);
    int_linear(coef, rc, IRT_EQ, pos[k]);
  }

  // every square holds exactly one number: pos is a permutation of the squares, and grid[s] is the number held by square s
  vec<IntVar*> grid;
  createVars(grid, cells, 0, cells - 1);
  inverse(pos, grid);

  // the move from each number to the next one is a type I or type II move
  vec<int> plusminus;
  plusminus.push(1); plusminus.push(-1);
  for (int k = 0; k + 1 < cells; ++k) {
    // dr and dc are the row and column change from number k+1 to number k+2
    IntVar* dr = newIntVar(-(n - 1), n - 1);
    IntVar* dc = newIntVar(-(n - 1), n - 1);
    vec<IntVar*> rows_pair;
    rows_pair.push(row[k + 1]); rows_pair.push(row[k]);
    int_linear(plusminus, rows_pair, IRT_EQ, dr);
    vec<IntVar*> cols_pair;
    cols_pair.push(col[k + 1]); cols_pair.push(col[k]);
    int_linear(plusminus, cols_pair, IRT_EQ, dc);

    // type I: three squares straight along a row or a column; type II: two squares diagonally
    vec<IntVar*> move;
    move.push(dr); move.push(dc);
    vec<vec<int>> allowed;
    int moves[8][2] = {{0, 3}, {0, -3}, {3, 0}, {-3, 0}, {2, 2}, {2, -2}, {-2, 2}, {-2, -2}};
    for (int m = 0; m < 8; ++m) {
      allowed.push();
      allowed.last().push(moves[m][0]);
      allowed.last().push(moves[m][1]);
    }
    table(move, allowed);
  }

  // the first number is free; branch on the squares of the numbers in order
  branch(pos, VAR_INORDER, VAL_MIN);

  // the grid is output as a list of rows; each cell holds the number in it (1 to n*n)
  json rows = json::array();
  for (int r = 0; r < n; ++r) {
    json rowjson = json::array();
    for (int c = 0; c < n; ++c) {
      IntVar* v = newIntVar(1, cells);
      vec<IntVar*> vv; vv.push(v); vv.push(grid[r * n + c]);
      vec<int> one_minus; one_minus.push(1); one_minus.push(-1);
      int_linear(one_minus, vv, IRT_EQ, 1);
      rowjson.push_back(dcp::out(v));
    }
    rows.push_back(rowjson);
  }
  outputs = {{"x", rows}};
}
