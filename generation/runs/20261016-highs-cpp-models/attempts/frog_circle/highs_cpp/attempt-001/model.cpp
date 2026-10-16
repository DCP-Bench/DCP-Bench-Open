// frog_circle: cards 1..n in a circle. The frog starts on card 1 and from each card k jumps
// k places clockwise. Find an arrangement x (x[p] is the card at circle place p, 0-based)
// such that the frog lands on every card.
//
// Model: the frog's visits form a Hamiltonian path over the places, starting at the place
// holding card 1. Each place p has at most one successor arc a[p][q] (the frog jumps from p
// to q, so card x[p] = (q - p) mod n). The last place on the path holds card n (it is the
// only place with no jump to make, and the cards 1..n-1 are used by the jumps).
// A single path with no cycles is enforced by Miller-Tucker-Zemlin order variables.

#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const int n = instance.at("n").get<int>();
  const double M = n;  // big-M from the instance size: the order values lie in 0..n-1

  // ---- columns ----
  // y[p][v-1] = 1 when place p holds card v
  std::vector<std::vector<dcp::Lin>> y(n, std::vector<dcp::Lin>(n));
  for (int p = 0; p < n; ++p)
    for (int v = 0; v < n; ++v) y[p][v] = dcp::new_var(h, 0, 1);

  // x[p] is the card at place p
  std::vector<dcp::Lin> x(n);
  for (int p = 0; p < n; ++p) x[p] = dcp::new_var(h, 1, n);

  // a[p][q] = 1 when the frog jumps from place p to place q (p != q)
  std::vector<std::vector<dcp::Lin>> a(n, std::vector<dcp::Lin>(n));
  for (int p = 0; p < n; ++p)
    for (int q = 0; q < n; ++q)
      if (p != q) a[p][q] = dcp::new_var(h, 0, 1);

  // e[p] = 1 when place p is the last place the frog lands on
  std::vector<dcp::Lin> e(n);
  for (int p = 0; p < n; ++p) e[p] = dcp::new_var(h, 0, 1);

  // st[p] = 1 when place p holds card 1, where the frog starts
  std::vector<dcp::Lin> st(n);
  for (int p = 0; p < n; ++p) st[p] = dcp::new_var(h, 0, 1);

  // ord[p] = position of place p on the frog's path, 0 at the start
  std::vector<dcp::Lin> ord(n);
  for (int p = 0; p < n; ++p) ord[p] = dcp::new_var(h, 0, n - 1);

  // ---- each place holds exactly one card, and each card is used once ----
  // // every place holds exactly one card
  for (int p = 0; p < n; ++p) {
    dcp::Lin s;
    for (int v = 0; v < n; ++v) s = s + y[p][v];
    dcp::add_row(h, s, 1, 1);
  }
  // // every card sits on exactly one place
  for (int v = 0; v < n; ++v) {
    dcp::Lin s;
    for (int p = 0; p < n; ++p) s = s + y[p][v];
    dcp::add_row(h, s, 1, 1);
  }
  // // x[p] is the card number given by y[p]
  for (int p = 0; p < n; ++p) {
    dcp::Lin s = x[p];
    for (int v = 0; v < n; ++v) s = s - (v + 1) * y[p][v];
    dcp::add_row(h, s, 0, 0);
  }

  // ---- the frog's path ----
  // // each place has one outgoing jump, or is the last place of the path
  for (int p = 0; p < n; ++p) {
    dcp::Lin s = e[p];
    for (int q = 0; q < n; ++q)
      if (q != p) s = s + a[p][q];
    dcp::add_row(h, s, 1, 1);
  }
  // // each place has one incoming jump, or is the start of the path
  for (int q = 0; q < n; ++q) {
    dcp::Lin s = st[q];
    for (int p = 0; p < n; ++p)
      if (p != q) s = s + a[p][q];
    dcp::add_row(h, s, 1, 1);
  }
  // // exactly one start and exactly one last place
  {
    dcp::Lin s, t;
    for (int p = 0; p < n; ++p) {
      s = s + st[p];
      t = t + e[p];
    }
    dcp::add_row(h, s, 1, 1);
    dcp::add_row(h, t, 1, 1);
  }
  // // a jump from place p to place q is a card of (q - p) places clockwise: x[p] = (q - p) mod n
  // // the last place of the path holds card n, which has no jump to make
  for (int p = 0; p < n; ++p) {
    dcp::Lin s = x[p] - n * e[p];
    for (int q = 0; q < n; ++q)
      if (q != p) s = s - ((q - p + n) % n) * a[p][q];
    dcp::add_row(h, s, 0, 0);
  }
  // // the start place holds card 1
  for (int p = 0; p < n; ++p) {
    dcp::Lin s = x[p] + (n - 1) * st[p];
    dcp::add_row(h, s, -kHighsInf, n);
  }
  // // the start place is first on the path, the order of the other places is set by the jumps
  for (int p = 0; p < n; ++p) {
    dcp::Lin s = ord[p] + (n - 1) * st[p];
    dcp::add_row(h, s, -kHighsInf, n - 1);
  }
  // // every jump goes to a place one step later on the path, so the path has no cycle
  for (int p = 0; p < n; ++p)
    for (int q = 0; q < n; ++q)
      if (q != p) {
        // ord[q] >= ord[p] + 1 - M (1 - a[p][q])
        dcp::Lin s = ord[q] - ord[p] - M * a[p][q];
        dcp::add_row(h, s, 1 - M, kHighsInf);
      }

  // // the arrangement starts with card 1 in the first place, so that the list is fixed up to rotation
  dcp::add_row(h, x[0], 1, 1);

  // ---- outputs ----
  // // the arrangement x: the card at each place, in circle order
  out.add("x", x);
}
