// Magic square of size n (n != 2): an n x n grid of different integers 1..n^2 where
// every row, every column and both diagonals sum to n(n^2+1)/2. The instance gives n.
// Output square[i][j] is the cell in row i and column j (0-based), holding an integer.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const int n = instance.at("n").get<int>();
  const int cells = n * n;           // there are n^2 cells and n^2 values
  const int magic = n * (cells + 1) / 2;  // n(n^2+1)/2

  // y[c][v] = 1 when cell c holds the value v+1.
  std::vector<std::vector<dcp::Lin>> y(cells, std::vector<dcp::Lin>(cells));
  for (int c = 0; c < cells; ++c)
    for (int v = 0; v < cells; ++v) y[c][v] = dcp::new_var(h, 0, 1);

  // x[c] is the value in cell c, in 1..n^2.
  std::vector<dcp::Lin> x(cells);
  for (int c = 0; c < cells; ++c) x[c] = dcp::new_var(h, 1, cells);

  // each cell holds exactly one value: x[c] = sum_v (v+1) y[c][v], sum_v y[c][v] = 1
  for (int c = 0; c < cells; ++c) {
    dcp::Lin link = x[c];
    dcp::Lin one_value;
    for (int v = 0; v < cells; ++v) {
      link = link - static_cast<double>(v + 1) * y[c][v];
      one_value = one_value + y[c][v];
    }
    dcp::add_row(h, link, 0, 0);
    dcp::add_row(h, one_value, 1, 1);
  }

  // every value 1..n^2 is used by exactly one cell (so all cells differ)
  for (int v = 0; v < cells; ++v) {
    dcp::Lin used;
    for (int c = 0; c < cells; ++c) used = used + y[c][v];
    dcp::add_row(h, used, 1, 1);
  }

  // every row sums to n(n^2+1)/2
  for (int i = 0; i < n; ++i) {
    dcp::Lin sum;
    for (int j = 0; j < n; ++j) sum = sum + x[i * n + j];
    dcp::add_row(h, sum, magic, magic);
  }

  // every column sums to n(n^2+1)/2
  for (int j = 0; j < n; ++j) {
    dcp::Lin sum;
    for (int i = 0; i < n; ++i) sum = sum + x[i * n + j];
    dcp::add_row(h, sum, magic, magic);
  }

  // the main diagonal sums to n(n^2+1)/2
  dcp::Lin diagonal;
  for (int i = 0; i < n; ++i) diagonal = diagonal + x[i * n + i];
  dcp::add_row(h, diagonal, magic, magic);

  // the other diagonal sums to n(n^2+1)/2
  dcp::Lin anti_diagonal;
  for (int i = 0; i < n; ++i) anti_diagonal = anti_diagonal + x[i * n + (n - 1 - i)];
  dcp::add_row(h, anti_diagonal, magic, magic);

  std::vector<std::vector<dcp::Lin>> square(n, std::vector<dcp::Lin>(n));
  for (int i = 0; i < n; ++i)
    for (int j = 0; j < n; ++j) square[i][j] = x[i * n + j];
  out.add("square", square);
}
