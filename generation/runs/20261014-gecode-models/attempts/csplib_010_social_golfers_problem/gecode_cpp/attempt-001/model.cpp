#include "dcp.h"

// Social golfers: groups * groupSize golfers play once a week for n_weeks weeks,
// in groups of group_size. No two golfers share a group more than once.
class SocialGolfers : public dcp::Space {
 protected:
  int golfers;      // n_groups * group_size
  int weeks;        // n_weeks
  int groups;       // n_groups
  int groupSize;    // group_size
  IntVarArray x;    // x[i * weeks + j]: group of golfer i in week j

 public:
  explicit SocialGolfers(const json& instance) {
    weeks = instance.at("n_weeks").get<int>();
    groups = instance.at("n_groups").get<int>();
    groupSize = instance.at("group_size").get<int>();
    golfers = groups * groupSize;

    x = IntVarArray(*this, golfers * weeks, 0, groups - 1);
    Matrix<IntVarArray> assign(x, weeks, golfers);

    for (int j = 0; j < weeks; ++j) {
      IntVarArgs week;
      for (int i = 0; i < golfers; ++i) week << x[i * weeks + j];

      // every group holds exactly group_size golfers in each week
      for (int k = 0; k < groups; ++k) count(*this, week, k, IRT_EQ, groupSize);

      // group numbers are interchangeable within a week: a group is numbered
      // only after the one before it has appeared
      precede(*this, week, IntArgs::create(groups, 0, 1));
    }

    // no two golfers play in the same group on more than one occasion:
    // count the weeks in which a pair shares a group and allow at most one
    for (int a = 0; a < golfers; ++a)
      for (int b = a + 1; b < golfers; ++b) {
        BoolVarArgs together;
        for (int j = 0; j < weeks; ++j)
          together << expr(*this, x[a * weeks + j] == x[b * weeks + j]);
        linear(*this, together, IRT_LQ, 1);
      }

    branch(*this, x, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    output("assign", assign);
  }

  SocialGolfers(SocialGolfers& s) : dcp::Space(s) {
    golfers = s.golfers;
    weeks = s.weeks;
    groups = s.groups;
    groupSize = s.groupSize;
    x.update(*this, s.x);
  }
  Gecode::Space* copy() override { return new SocialGolfers(*this); }
};

DCP_MODEL(SocialGolfers)
