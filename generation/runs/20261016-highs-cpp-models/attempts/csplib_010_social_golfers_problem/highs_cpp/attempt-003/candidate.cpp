#include "dcp.h"

// Social golfers: the club has n_groups * group_size golfers, each plays once a week
// in a group of group_size golfers, for n_weeks weeks. No two golfers may share a group
// on more than one occasion. assign[i][w] is the group of golfer i in week w, 0-based.
void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int n_weeks = instance.at("n_weeks").get<int>();
  int n_groups = instance.at("n_groups").get<int>();
  int group_size = instance.at("group_size").get<int>();
  int n_golfers = n_groups * group_size;

  // play[i][w][g] is 1 when golfer i plays in group g in week w
  std::vector<std::vector<std::vector<dcp::Lin>>> play(
      n_golfers, std::vector<std::vector<dcp::Lin>>(
                     n_weeks, std::vector<dcp::Lin>(n_groups)));
  for (int i = 0; i < n_golfers; i++)
    for (int w = 0; w < n_weeks; w++)
      for (int g = 0; g < n_groups; g++)
        play[i][w][g] = dcp::new_var(h, 0, 1);

  // each golfer plays in exactly one group each week
  for (int i = 0; i < n_golfers; i++)
    for (int w = 0; w < n_weeks; w++) {
      dcp::Lin one_group;
      for (int g = 0; g < n_groups; g++) one_group = one_group + play[i][w][g];
      dcp::add_row(h, one_group, 1, 1);
    }

  // each group holds exactly group_size golfers each week
  for (int w = 0; w < n_weeks; w++)
    for (int g = 0; g < n_groups; g++) {
      dcp::Lin members;
      for (int i = 0; i < n_golfers; i++) members = members + play[i][w][g];
      dcp::add_row(h, members, group_size, group_size);
    }

  // together[i][j][w] is 1 when golfers i and j play in the same group in week w
  // (it is forced to 1 by each shared group; it may be 1 without a shared group, which
  // only tightens the no-meeting rule below)
  std::vector<std::vector<std::vector<dcp::Lin>>> together(
      n_golfers, std::vector<std::vector<dcp::Lin>>(
                     n_golfers, std::vector<dcp::Lin>(n_weeks)));
  for (int i = 0; i < n_golfers; i++)
    for (int j = i + 1; j < n_golfers; j++)
      for (int w = 0; w < n_weeks; w++) {
        dcp::Lin t = dcp::new_var(h, 0, 1);
        // together >= play[i][w][g] + play[j][w][g] - 1, for each group g
        for (int g = 0; g < n_groups; g++)
          dcp::add_row(h, t - play[i][w][g] - play[j][w][g], -1, kHighsInf);
        together[i][j][w] = t;
        together[j][i][w] = t;
      }

  // no two golfers play in the same group in more than one week
  for (int i = 0; i < n_golfers; i++)
    for (int j = i + 1; j < n_golfers; j++) {
      dcp::Lin meetings;
      for (int w = 0; w < n_weeks; w++) meetings = meetings + together[i][j][w];
      dcp::add_row(h, meetings, -kHighsInf, 1);
    }

  // each golfer has at least group_size - 1 group mates each week
  // (implied: the golfer shares its group with group_size - 1 others)
  for (int i = 0; i < n_golfers; i++)
    for (int w = 0; w < n_weeks; w++) {
      dcp::Lin mates;
      for (int j = 0; j < n_golfers; j++)
        if (j != i) mates = mates + together[i][j][w];
      dcp::add_row(h, mates, group_size - 1, kHighsInf);
    }

  // the output: group number of each golfer in each week, 0-based
  std::vector<std::vector<dcp::Lin>> assign(n_golfers, std::vector<dcp::Lin>(n_weeks));
  for (int i = 0; i < n_golfers; i++)
    for (int w = 0; w < n_weeks; w++) {
      dcp::Lin group_no;
      for (int g = 0; g < n_groups; g++) group_no = group_no + double(g) * play[i][w][g];
      assign[i][w] = group_no;
    }
  out.add("assign", assign);
}
