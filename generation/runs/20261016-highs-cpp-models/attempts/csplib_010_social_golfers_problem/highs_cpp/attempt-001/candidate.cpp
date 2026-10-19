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

  // two golfers who share a group in a week are counted as meeting that week
  // (the indicator is forced to 1 when both golfers are in the same group)
  // no two golfers meet in more than one week
  for (int i = 0; i < n_golfers; i++)
    for (int j = i + 1; j < n_golfers; j++) {
      dcp::Lin meetings;
      for (int w = 0; w < n_weeks; w++) {
        dcp::Lin together = dcp::new_var(h, 0, 1);
        for (int g = 0; g < n_groups; g++)
          // together >= play[i][w][g] + play[j][w][g] - 1
          dcp::add_row(h, together - play[i][w][g] - play[j][w][g], -1, kHighsInf);
        meetings = meetings + together;
      }
      // golfers i and j meet in at most one week
      dcp::add_row(h, meetings, -kHighsInf, 1);
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
