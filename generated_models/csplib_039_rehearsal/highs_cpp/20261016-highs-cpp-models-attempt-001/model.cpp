// CSPLib 039 rehearsal: a concert has pieces of music of different durations, each
// involving a different set of orchestra players. Players arrive immediately before the
// first piece they are in and leave immediately after the last one. Find the rehearsal
// order of the pieces that minimises the total time players are present but not playing.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const std::vector<int> duration = instance.at("duration").get<std::vector<int>>();
  const json& rehearsal = instance.at("rehearsal");
  const int n = static_cast<int>(duration.size());  // number of pieces
  const int m = static_cast<int>(rehearsal.size());  // number of players

  // Total duration of all pieces. A schedule without gaps ends by then, so every start
  // lies in [0, H - d] and H is a valid big-M for the non-overlap rows.
  double H = 0;
  for (int d : duration) H += d;

  // Start time of each piece, in [0, H - d_p].
  std::vector<dcp::Lin> start(n);
  for (int p = 0; p < n; ++p) start[p] = dcp::new_var(h, 0, H - duration[p], false);

  // order[p][q] for p < q: 1 when piece p is rehearsed before piece q.
  std::vector<std::vector<dcp::Lin>> before(n, std::vector<dcp::Lin>(n));
  for (int p = 0; p < n; ++p)
    for (int q = p + 1; q < n; ++q) before[p][q] = dcp::new_var(h, 0, 1);

  // slot[p][s] = 1 when piece p is rehearsed in slot s (0-based).
  std::vector<std::vector<dcp::Lin>> slot(n, std::vector<dcp::Lin>(n));
  for (int p = 0; p < n; ++p)
    for (int s = 0; s < n; ++s) slot[p][s] = dcp::new_var(h, 0, 1);

  // No two pieces overlap: the one rehearsed first ends before the other starts.
  // With y = 1 (p before q): start[q] >= start[p] + d_p. With y = 0: start[p] >= start[q] + d_q.
  for (int p = 0; p < n; ++p) {
    for (int q = p + 1; q < n; ++q) {
      dcp::Lin y = before[p][q];
      dcp::add_row(h, start[q] - start[p] - H * y, duration[p] - H, kHighsInf);
      dcp::add_row(h, start[p] - start[q] + H * y, duration[q], kHighsInf);
    }
  }

  // Each piece has exactly one slot, and each slot holds exactly one piece.
  for (int p = 0; p < n; ++p) {
    dcp::Lin one;
    for (int s = 0; s < n; ++s) one = one + slot[p][s];
    dcp::add_row(h, one, 1, 1);
  }
  for (int s = 0; s < n; ++s) {
    dcp::Lin one;
    for (int p = 0; p < n; ++p) one = one + slot[p][s];
    dcp::add_row(h, one, 1, 1);
  }

  // The slot of piece p is the number of pieces rehearsed before it.
  // A piece q before p is y[q][p] when q < p, and 1 - y[p][q] when q > p.
  for (int p = 0; p < n; ++p) {
    dcp::Lin position;
    for (int q = 0; q < n; ++q) {
      if (q < p) position = position + before[q][p];
      else if (q > p) position = position + (1.0 - before[p][q]);
    }
    dcp::Lin slot_index;
    for (int s = 0; s < n; ++s) slot_index = slot_index + double(s) * slot[p][s];
    dcp::add_row(h, slot_index - position, 0, 0);
  }

  // Players. The first piece a player is in starts at or after F_i, and the last one
  // ends at or before L_i. Waiting time for player i is L_i - F_i minus the time
  // the player plays. Both F_i and L_i are pushed to their tight values by the objective,
  // so they only need the one-sided rows below.
  dcp::Lin objective;
  double playing = 0;
  for (int i = 0; i < m; ++i) {
    const json& row = rehearsal[i];
    bool plays = false;
    for (int p = 0; p < n; ++p)
      if (row[p].get<int>() == 1) plays = true;
    if (!plays) continue;

    // first[i] <= start of each piece player i is in
    dcp::Lin first = dcp::new_var(h, 0, H, false);
    // last[i] >= end of each piece player i is in
    dcp::Lin last = dcp::new_var(h, 0, H, false);
    for (int p = 0; p < n; ++p) {
      if (row[p].get<int>() != 1) continue;
      dcp::add_row(h, first - start[p], -kHighsInf, 0);
      dcp::add_row(h, last - start[p], duration[p], kHighsInf);
      playing += duration[p];
    }
    objective = objective + last - first;
  }
  // Subtract the time players spend playing, which is fixed by the data.
  objective = objective - playing;

  out.minimize(objective);

  // The rehearsal order: slot s holds the piece p with slot[p][s] = 1.
  std::vector<dcp::Lin> order(n);
  for (int s = 0; s < n; ++s) {
    dcp::Lin piece;
    for (int p = 0; p < n; ++p) piece = piece + double(p) * slot[p][s];
    order[s] = piece;
  }
  out.add("rehearsal_order", order);
}
