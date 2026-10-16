#include "dcp.h"

// Letters are A=1, C=2, G=3, T=4. letter[i][p][u] is 1 when word i has letter u+1 at position p.
// The Watson-Crick complement of letter u+1 is letter 4-u, that is index 3-u.

// Returns z with z = 1 when both a and b are 1 and z = 0 otherwise (a, b binary).
static dcp::Lin both(Highs& h, const dcp::Lin& a, const dcp::Lin& b) {
  dcp::Lin z = dcp::new_var(h, 0, 1, false);
  // z is at most each of a and b
  dcp::add_row(h, z - a, -kHighsInf, 0);
  dcp::add_row(h, z - b, -kHighsInf, 0);
  // z is at least a + b - 1
  dcp::add_row(h, z - a - b, -1, kHighsInf);
  return z;
}

// Number of positions where the two words agree is at most n - 4, so the words differ in at least 4 positions.
static void at_most_agreements(Highs& h, const dcp::Lin& agreements, int limit) {
  dcp::add_row(h, agreements, -kHighsInf, limit);
}

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int n = instance.at("n").get<int>();
  int m = instance.at("num_words").get<int>();

  // Each position of each word holds exactly one letter (one-hot over A, C, G, T).
  std::vector<std::vector<std::vector<dcp::Lin>>> letter(
      m, std::vector<std::vector<dcp::Lin>>(n, std::vector<dcp::Lin>(4)));
  for (int i = 0; i < m; i++)
    for (int p = 0; p < n; p++) {
      dcp::Lin one_hot;
      for (int u = 0; u < 4; u++) {
        letter[i][p][u] = dcp::new_var(h, 0, 1);
        one_hot = one_hot + letter[i][p][u];
      }
      dcp::add_row(h, one_hot, 1, 1);
    }

  // Each word has exactly four symbols from {C, G}.
  for (int i = 0; i < m; i++) {
    dcp::Lin cg;
    for (int p = 0; p < n; p++) cg = cg + letter[i][p][1] + letter[i][p][2];
    dcp::add_row(h, cg, 4, 4);
  }

  // Each pair of distinct words differs in at least 4 positions.
  for (int i = 0; i < m; i++)
    for (int j = i + 1; j < m; j++) {
      dcp::Lin agreements;
      for (int p = 0; p < n; p++)
        for (int u = 0; u < 4; u++)
          agreements = agreements + both(h, letter[i][p][u], letter[j][p][u]);
      at_most_agreements(h, agreements, n - 4);
    }

  // For every pair x, y (x may equal y), the reverse of x and the complement of y differ in at least 4 positions.
  // The reverse of x at position p is x[n-1-p]; the complement of y at position p is letter 3-u where y[p] has letter u.
  for (int i = 0; i < m; i++)
    for (int j = 0; j < m; j++) {
      dcp::Lin agreements;
      for (int p = 0; p < n; p++)
        for (int u = 0; u < 4; u++)
          agreements = agreements + both(h, letter[i][n - 1 - p][u], letter[j][p][3 - u]);
      at_most_agreements(h, agreements, n - 4);
    }

  // The output words: each cell is its letter number, 1 for A, 2 for C, 3 for G, 4 for T.
  std::vector<std::vector<dcp::Lin>> words(m, std::vector<dcp::Lin>(n));
  for (int i = 0; i < m; i++)
    for (int p = 0; p < n; p++) {
      dcp::Lin cell;
      for (int u = 0; u < 4; u++) cell = cell + (double)(u + 1) * letter[i][p][u];
      words[i][p] = cell;
    }
  out.add("words", words);
}
