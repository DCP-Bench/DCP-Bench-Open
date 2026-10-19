#include "dcp.h"

#include <algorithm>
#include <vector>

// Block lengths of one line, in order. Zeros are padding and are skipped.
static std::vector<int> block_lengths(const json& rule) {
  std::vector<int> blocks;
  for (const auto& v : rule) {
    int len = v.get<int>();
    if (len > 0) blocks.push_back(len);
  }
  return blocks;
}

// Shades the cells of one line so that its runs of shaded squares are exactly the
// blocks, in order, with at least one unshaded square between consecutive blocks.
static void add_line(Highs& h, const std::vector<dcp::Lin>& cells, const std::vector<int>& blocks) {
  const int len = static_cast<int>(cells.size());
  const int k_count = static_cast<int>(blocks.size());

  // start[k][p] = 1 when block k begins at square p; start_pos[k] is its start position.
  std::vector<std::vector<dcp::Lin>> start(k_count);
  std::vector<dcp::Lin> start_pos(k_count);
  for (int k = 0; k < k_count; ++k) {
    // each block begins at exactly one position
    dcp::Lin one_start;
    dcp::Lin pos;
    for (int p = 0; p + blocks[k] <= len; ++p) {
      dcp::Lin s = dcp::new_var(h, 0, 1);
      start[k].push_back(s);
      one_start = one_start + s;
      pos = pos + double(p) * s;
    }
    dcp::add_row(h, one_start, 1, 1);
    start_pos[k] = pos;
  }

  // blocks keep their order, and the square after a block is unshaded
  for (int k = 0; k + 1 < k_count; ++k) {
    // block k+1 starts at least one square after block k ends
    dcp::add_row(h, start_pos[k + 1] - start_pos[k], blocks[k] + 1, kHighsInf);
  }

  // a square is shaded exactly when some block covers it
  for (int j = 0; j < len; ++j) {
    dcp::Lin cover;
    for (int k = 0; k < k_count; ++k) {
      int first = std::max(0, j - blocks[k] + 1);
      int last = std::min(j, len - blocks[k]);
      for (int p = first; p <= last; ++p) cover = cover + start[k][p];
    }
    // shaded square j is covered by exactly one block
    dcp::add_row(h, cells[j] - cover, 0, 0);
  }
}

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const int rows = instance.at("rows").get<int>();
  const int cols = instance.at("cols").get<int>();
  const json& row_rules = instance.at("row_rules");
  const json& col_rules = instance.at("col_rules");

  // board[i][j] = 1 when square (i, j) is shaded
  std::vector<std::vector<dcp::Lin>> board(rows, std::vector<dcp::Lin>(cols));
  for (int i = 0; i < rows; ++i)
    for (int j = 0; j < cols; ++j) board[i][j] = dcp::new_var(h, 0, 1);

  // each row's runs of shaded squares follow the row's clue
  for (int i = 0; i < rows; ++i) {
    add_line(h, board[i], block_lengths(row_rules[i]));
  }

  // each column's runs of shaded squares follow the column's clue
  for (int j = 0; j < cols; ++j) {
    std::vector<dcp::Lin> column(rows);
    for (int i = 0; i < rows; ++i) column[i] = board[i][j];
    add_line(h, column, block_lengths(col_rules[j]));
  }

  out.add("board", board);
}
