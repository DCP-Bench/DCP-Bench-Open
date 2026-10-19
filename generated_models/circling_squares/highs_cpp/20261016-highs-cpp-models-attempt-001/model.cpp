// Circling the squares: place a different number in each of the ten squares A, B, C, D, E, F, G, H, I, K
// (in circle order) so that the squares of any two adjacent numbers sum to the sum of the squares of the
// two numbers diametrically opposite them. A=16, B=2, F=8, G=14 are fixed by the statement. Fractions are
// not allowed and no number needs more than two figures, so every number is an integer in 0..99.
// The instance has no data fields: the statement fixes everything, so build() ignores its argument.
#include "dcp.h"

namespace {

const int kSquares = 10;   // positions in the circle: 0=A, 1=B, 2=C, 3=D, 4=E, 5=F, 6=G, 7=H, 8=I, 9=K
const int kMaxValue = 99;  // "no number need contain more than two figures"
const int kValues = kMaxValue + 1;

}  // namespace

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  (void)instance;

  // y[p][v] = 1 when the square at position p holds the number v. Each square's value is the
  // one number it holds, so the value and its square are linear in these binaries.
  std::vector<std::vector<dcp::Lin>> y(kSquares, std::vector<dcp::Lin>(kValues));
  for (int p = 0; p < kSquares; ++p)
    for (int v = 0; v < kValues; ++v) y[p][v] = dcp::new_var(h, 0, 1);

  // Each square holds exactly one number.
  for (int p = 0; p < kSquares; ++p) {
    dcp::Lin one_value;
    for (int v = 0; v < kValues; ++v) one_value = one_value + y[p][v];
    dcp::add_row(h, one_value, 1, 1);
  }

  // A number is used in at most one square: every number differs from the others.
  for (int v = 0; v < kValues; ++v) {
    dcp::Lin used_once;
    for (int p = 0; p < kSquares; ++p) used_once = used_once + y[p][v];
    dcp::add_row(h, used_once, -kHighsInf, 1);
  }

  // The four numbers given by the statement: A=16, B=2, F=8, G=14.
  dcp::add_row(h, y[0][16], 1, 1);  // A = 16
  dcp::add_row(h, y[1][2], 1, 1);   // B = 2
  dcp::add_row(h, y[5][8], 1, 1);   // F = 8
  dcp::add_row(h, y[6][14], 1, 1);  // G = 14

  // Number and square of the square at each position, as expressions over the binaries.
  std::vector<dcp::Lin> number(kSquares), square(kSquares);
  for (int p = 0; p < kSquares; ++p) {
    for (int v = 0; v < kValues; ++v) {
      number[p] = number[p] + static_cast<double>(v) * y[p][v];
      square[p] = square[p] + static_cast<double>(v) * static_cast<double>(v) * y[p][v];
    }
  }

  // The squares of two adjacent numbers sum to the squares of the two numbers diametrically opposite them.
  // Opposite of position p is p + 5 (mod 10), so the pair (p, p+1) is opposite the pair (p+5, p+6).
  for (int p = 0; p < kSquares; ++p) {
    int q = (p + 1) % kSquares;
    int p_opp = (p + 5) % kSquares;
    int q_opp = (p + 6) % kSquares;
    dcp::add_row(h, square[p] + square[q] - square[p_opp] - square[q_opp], 0, 0);
  }

  const char* names[kSquares] = {"A", "B", "C", "D", "E", "F", "G", "H", "I", "K"};
  for (int p = 0; p < kSquares; ++p) out.add(names[p], number[p]);
}
