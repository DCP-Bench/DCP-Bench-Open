// Nonogram: shade squares of a grid so that every row and column shows its run-length clue.
#include <array>
#include <vector>

#include "dcp.h"

namespace {

// The blocks of one clue. Zeros in the instance are padding to a fixed length, so only the
// positive entries are blocks, in order.
std::vector<int> Blocks(const std::vector<int>& clue) {
  std::vector<int> blocks;
  for (int v : clue) {
    if (v > 0) blocks.push_back(v);
  }
  return blocks;
}

// Builds the automaton for one line: any number of unshaded squares, then the blocks in order
// with at least one unshaded square between consecutive blocks, then any unshaded squares.
// Symbols are 1 = unshaded and 2 = shaded, as Chuffed's regular constraint expects.
// States are numbered from 1; q0 is 1. d[s - 1][symbol - 1] is the next state, 0 rejects.
void BuildAutomaton(const std::vector<int>& blocks, int& q, vec<vec<int>>& d, vec<int>& accept) {
  int k = static_cast<int>(blocks.size());

  // gap[i]: all i blocks are placed and the line is in an unshaded run (i = 0 is the start)
  std::vector<int> gap(k + 1);
  // inside[i][j]: block i is being placed and j of its squares are shaded so far
  std::vector<std::vector<int>> inside(k);
  int next = 0;
  for (int i = 0; i <= k; ++i) gap[i] = ++next;
  for (int i = 0; i < k; ++i) {
    inside[i].assign(blocks[i] + 1, 0);
    for (int j = 1; j <= blocks[i]; ++j) inside[i][j] = ++next;
  }
  q = next;

  // trans[s][0] = next state on unshaded, trans[s][1] = next state on shaded
  std::vector<std::array<int, 2>> trans(q, std::array<int, 2>{0, 0});
  for (int i = 0; i <= k; ++i) {
    // an unshaded square keeps the gap; a shaded square starts block i if one is left
    trans[gap[i] - 1][0] = gap[i];
    if (i < k) trans[gap[i] - 1][1] = inside[i][1];
  }
  for (int i = 0; i < k; ++i) {
    for (int j = 1; j <= blocks[i]; ++j) {
      int s = inside[i][j] - 1;
      if (j < blocks[i]) {
        // a block continues with shaded squares until its length is reached
        trans[s][1] = inside[i][j + 1];
      } else {
        // the block is complete, so the next square must be unshaded and starts the gap after it
        trans[s][0] = gap[i + 1];
      }
    }
  }

  for (int s = 0; s < q; ++s) {
    d.push();
    d.last().push(trans[s][0]);
    d.last().push(trans[s][1]);
  }

  // the line may end in the gap after the last block, or right after the last block
  accept.push(gap[k]);
  if (k >= 1) accept.push(inside[k - 1][blocks[k - 1]]);
}

}  // namespace

void Build(const json& instance, json& outputs) {
  int rows = instance.at("rows");
  int cols = instance.at("cols");
  std::vector<std::vector<int>> row_rules = instance.at("row_rules").get<std::vector<std::vector<int>>>();
  std::vector<std::vector<int>> col_rules = instance.at("col_rules").get<std::vector<std::vector<int>>>();

  // code[r][c] is 1 for an unshaded square and 2 for a shaded one (the symbols of the automaton)
  vec<vec<IntVar*>> code;
  createVars(code, rows, cols, 1, 2, true);

  // board[r][c] is 1 for a shaded square and 0 otherwise (the output)
  vec<vec<IntVar*>> board;
  createVars(board, rows, cols, 0, 1, true);

  // the output is the shading code minus one: code = board + 1
  for (int r = 0; r < rows; ++r) {
    for (int c = 0; c < cols; ++c) {
      vec<int> shift;
      shift.push(1);
      shift.push(-1);
      vec<IntVar*> pair;
      pair.push(code[r][c]);
      pair.push(board[r][c]);
      int_linear(shift, pair, IRT_EQ, 1);
    }
  }

  // each row shows its run-length clue
  for (int r = 0; r < rows; ++r) {
    int q = 0;
    vec<vec<int>> d;
    vec<int> accept;
    BuildAutomaton(Blocks(row_rules[r]), q, d, accept);
    vec<IntVar*> line;
    for (int c = 0; c < cols; ++c) line.push(code[r][c]);
    regular(line, q, 2, d, 1, accept);
  }

  // each column shows its run-length clue
  for (int c = 0; c < cols; ++c) {
    int q = 0;
    vec<vec<int>> d;
    vec<int> accept;
    BuildAutomaton(Blocks(col_rules[c]), q, d, accept);
    vec<IntVar*> line;
    for (int r = 0; r < rows; ++r) line.push(code[r][c]);
    regular(line, q, 2, d, 1, accept);
  }

  // search over the squares in reading order
  vec<IntVar*> flat;
  flatten(code, flat);
  branch(flat, VAR_INORDER, VAL_MIN);

  json grid = json::array();
  for (int r = 0; r < rows; ++r) {
    json row = json::array();
    for (int c = 0; c < cols; ++c) row.push_back(dcp::out(board[r][c]));
    grid.push_back(row);
  }
  outputs = {{"board", grid}};
}
