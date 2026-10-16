// csplib_028_bibd: Balanced Incomplete Block Design (BIBD) with parameters (v, b, r, k, lambda).
// Find a v by b incidence matrix of 0s and 1s: every object occurs in exactly r blocks, every block
// contains exactly k objects, and every two distinct objects occur together in exactly lambda blocks.
// The output "matrix" is the incidence matrix: matrix[i][j] = 1 if object i is in block j.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int v = instance.at("v").get<int>();   // number of objects (rows of the matrix)
  int b = instance.at("b").get<int>();   // number of blocks (columns of the matrix)
  int r = instance.at("r").get<int>();   // each object occurs in r blocks
  int k = instance.at("k").get<int>();   // each block contains k objects
  int l = instance.at("l").get<int>();   // every two objects occur together in lambda blocks

  // the incidence matrix: x[i][j] = 1 if object i is in block j
  std::vector<std::vector<dcp::Lin>> x(v, std::vector<dcp::Lin>(b));
  for (int i = 0; i < v; i++)
    for (int j = 0; j < b; j++)
      x[i][j] = dcp::new_var(h, 0, 1);

  // each object occurs in exactly r different blocks
  for (int i = 0; i < v; i++) {
    dcp::Lin row = 0;
    for (int j = 0; j < b; j++) row = row + x[i][j];
    dcp::add_row(h, row, r, r);
  }

  // each block contains exactly k distinct objects
  for (int j = 0; j < b; j++) {
    dcp::Lin col = 0;
    for (int i = 0; i < v; i++) col = col + x[i][j];
    dcp::add_row(h, col, k, k);
  }

  // every two distinct objects occur together in exactly lambda blocks:
  // p[j] = x[i1][j] AND x[i2][j] is a binary product, linearised with three rows per block
  for (int i1 = 0; i1 < v; i1++) {
    for (int i2 = i1 + 1; i2 < v; i2++) {
      dcp::Lin together = 0;
      for (int j = 0; j < b; j++) {
        dcp::Lin p = dcp::new_var(h, 0, 1);
        dcp::add_row(h, p - x[i1][j], -kHighsInf, 0);        // p <= x[i1][j]
        dcp::add_row(h, p - x[i2][j], -kHighsInf, 0);        // p <= x[i2][j]
        dcp::add_row(h, p - x[i1][j] - x[i2][j], -1, kHighsInf);  // p >= x[i1][j] + x[i2][j] - 1
        together = together + p;
      }
      dcp::add_row(h, together, l, l);
    }
  }

  out.add("matrix", x);
}
