// Nontransitive dice: five dice with six faces each, face values 1..12.
// Die A beats die B when A has a strictly larger face than B in more than half
// of the 36 face pairs. The ten beats relationships fix the direction for every
// pair of the five dice (rows: Rock, Paper, Scissors, Lizard, Spock = 0..4).
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const int dice = 5;
  const int faces = 6;
  const int lo = 1;
  const int hi = 12;

  // face values of each die, each between 1 and 12 inclusive
  std::vector<std::vector<dcp::Lin>> dice_vals(dice, std::vector<dcp::Lin>(faces));
  for (int d = 0; d < dice; d++)
    for (int f = 0; f < faces; f++)
      dice_vals[d][f] = dcp::new_var(h, lo, hi);

  // beats relationships (0-based die indices): Rock(0) beats Scissors(2) and Lizard(3),
  // Paper(1) beats Rock(0) and Spock(4), Scissors(2) beats Paper(1) and Lizard(3),
  // Lizard(3) beats Paper(1) and Spock(4), Spock(4) beats Rock(0) and Scissors(2)
  const int beats[10][2] = {
      {0, 2}, {0, 3}, {1, 0}, {1, 4}, {2, 1},
      {2, 3}, {3, 1}, {3, 4}, {4, 0}, {4, 2},
  };

  // a die beats another when more than half of the 36 face pairs are strictly larger:
  // at least 19 pairs (p, q) with a_p >= b_q + 1
  // each pair gets a binary z that may be 1 only when a_p > b_q; M = 12 covers the
  // range of a_p - b_q - 1, which is -12..10 for values in 1..12
  const int big_m = hi - lo + 1;
  for (int r = 0; r < 10; r++) {
    int a = beats[r][0];
    int b = beats[r][1];
    // the number of strictly larger face pairs of die a over die b
    std::vector<dcp::Lin> indicators;
    for (int p = 0; p < faces; p++) {
      for (int q = 0; q < faces; q++) {
        // z = 1 implies a_p >= b_q + 1
        dcp::Lin z = dcp::new_var(h, 0, 1);
        // a_p - b_q - 1 >= -M (1 - z), i.e. a_p - b_q - M z >= 1 - M
        dcp::add_row(h, dice_vals[a][p] - dice_vals[b][q] - big_m * z, 1 - big_m, kHighsInf);
        indicators.push_back(z);
      }
    }
    // at least 19 of the 36 face pairs are strictly larger for die a
    dcp::Lin total = 0;
    for (const dcp::Lin& z : indicators) total = total + z;
    dcp::add_row(h, total, 19, kHighsInf);
  }

  // the dice, one row per die in the order Rock, Paper, Scissors, Lizard, Spock
  out.add("dice", dice_vals);
}
