// csplib_049_number_partitioning: partition the numbers 1..N into two sets A and B
// such that A and B have the same cardinality, the sum of numbers in A equals the
// sum of numbers in B, and the sum of squares in A equals the sum of squares in B.
// Output A and B, each listed in increasing order (n/2 numbers each).
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int n = instance.at("n").get<int>();
  int half = n / 2;

  // x[i] is 1 when the number i (1..n) is in A, and 0 when it is in B.
  std::vector<dcp::Lin> x(n + 1);
  for (int i = 1; i <= n; ++i) x[i] = dcp::new_var(h, 0, 1);

  // A and B have the same cardinality (for odd N the bound is fractional and the model is infeasible)
  {
    dcp::Lin count;
    for (int i = 1; i <= n; ++i) count = count + x[i];
    dcp::add_row(h, count, n / 2.0, n / 2.0);
  }

  // Sum of numbers in A = sum of numbers in B: sum of A equals half of 1..N
  {
    double total = n * (n + 1) / 2.0;
    dcp::Lin sum_a;
    for (int i = 1; i <= n; ++i) sum_a = sum_a + (double)i * x[i];
    dcp::add_row(h, sum_a, total / 2.0, total / 2.0);
  }

  // Sum of squares of numbers in A = sum of squares of numbers in B: sum of squares in A is half of the total
  {
    double total = 0;
    for (int i = 1; i <= n; ++i) total += (double)i * i;
    dcp::Lin sq_a;
    for (int i = 1; i <= n; ++i) sq_a = sq_a + ((double)i * i) * x[i];
    dcp::add_row(h, sq_a, total / 2.0, total / 2.0);
  }

  // The positions of A in increasing order: y[k][i] is 1 when the k-th smallest element of A is the number i.
  std::vector<std::vector<dcp::Lin>> y(half, std::vector<dcp::Lin>(n + 1));
  for (int k = 0; k < half; ++k)
    for (int i = 1; i <= n; ++i) y[k][i] = dcp::new_var(h, 0, 1);

  // each position of A holds exactly one number
  for (int k = 0; k < half; ++k) {
    dcp::Lin one;
    for (int i = 1; i <= n; ++i) one = one + y[k][i];
    dcp::add_row(h, one, 1, 1);
  }

  // each number of A occupies exactly one position, and a number is in A exactly when x says so
  for (int i = 1; i <= n; ++i) {
    dcp::Lin placed;
    for (int k = 0; k < half; ++k) placed = placed + y[k][i];
    dcp::add_row(h, placed - x[i], 0, 0);
  }

  // the positions of A are strictly increasing
  std::vector<dcp::Lin> a(half);
  for (int k = 0; k < half; ++k)
    for (int i = 1; i <= n; ++i) a[k] = a[k] + (double)i * y[k][i];
  for (int k = 0; k + 1 < half; ++k) dcp::add_row(h, a[k + 1] - a[k], 1, kHighsInf);

  // The positions of B in increasing order: z[k][i] is 1 when the k-th smallest element of B is the number i.
  std::vector<std::vector<dcp::Lin>> z(half, std::vector<dcp::Lin>(n + 1));
  for (int k = 0; k < half; ++k)
    for (int i = 1; i <= n; ++i) z[k][i] = dcp::new_var(h, 0, 1);

  // each position of B holds exactly one number
  for (int k = 0; k < half; ++k) {
    dcp::Lin one;
    for (int i = 1; i <= n; ++i) one = one + z[k][i];
    dcp::add_row(h, one, 1, 1);
  }

  // each number of B occupies exactly one position, and a number is in B exactly when x says it is not in A
  for (int i = 1; i <= n; ++i) {
    dcp::Lin placed;
    for (int k = 0; k < half; ++k) placed = placed + z[k][i];
    dcp::add_row(h, placed + x[i], 1, 1);
  }

  // the positions of B are strictly increasing
  std::vector<dcp::Lin> b(half);
  for (int k = 0; k < half; ++k)
    for (int i = 1; i <= n; ++i) b[k] = b[k] + (double)i * z[k][i];
  for (int k = 0; k + 1 < half; ++k) dcp::add_row(h, b[k + 1] - b[k], 1, kHighsInf);

  out.add("A", a);
  out.add("B", b);
}
