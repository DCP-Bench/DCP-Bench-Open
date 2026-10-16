// Social golfers: schedule golfers into groups each week so that no two golfers share a group more than once.
// The club has n_groups groups of group_size golfers each week, for n_weeks weeks.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int n_weeks = instance.at("n_weeks");
  int n_groups = instance.at("n_groups");
  int group_size = instance.at("group_size");
  int golfers = n_groups * group_size;

  // assign[i][w] is the group (0 to n_groups-1) of golfer i in week w
  vec<vec<IntVar*>> assign;
  createVars(assign, golfers, n_weeks, 0, n_groups - 1, true);

  // every week each group holds exactly group_size golfers
  // members are the golfers that sit in group g this week (one Boolean per golfer)
  for (int w = 0; w < n_weeks; ++w) {
    for (int g = 0; g < n_groups; ++g) {
      vec<BoolView> members;
      for (int i = 0; i < golfers; ++i) {
        BoolView in = newBoolVar();
        int_rel_reif(assign[i][w], IRT_EQ, g, in);
        members.push(in);
      }
      // the number of golfers in group g this week is group_size
      bool_linear(members, IRT_EQ, getConstant(group_size));
    }
  }

  // two golfers may share a group in at most one week
  // meets[i][j][w] is true when golfers i and j are in the same group in week w
  for (int i = 0; i < golfers; ++i) {
    for (int j = i + 1; j < golfers; ++j) {
      vec<BoolView> together;
      for (int w = 0; w < n_weeks; ++w) {
        BoolView meet = newBoolVar();
        int_rel_reif(assign[i][w], IRT_EQ, assign[j][w], meet);
        together.push(meet);
      }
      // golfers i and j meet in at most one week
      bool_linear(together, IRT_LE, getConstant(1));
    }
  }

  // branch on the assignments week by week, golfer by golfer
  vec<IntVar*> flat;
  flatten(assign, flat);
  branch(flat, VAR_INORDER, VAL_MIN);

  json rows = json::array();
  for (int i = 0; i < golfers; ++i) {
    json row = json::array();
    for (int w = 0; w < n_weeks; ++w) row.push_back(dcp::out(assign[i][w]));
    rows.push_back(row);
  }
  outputs = {{"assign", rows}};
}
