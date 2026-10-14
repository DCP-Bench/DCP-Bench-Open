#include "dcp.h"

// Media selection: choose advertising media so that every target audience is
// reached by at least one selected medium, at minimum total campaign cost.
class MediaSelection : public dcp::Space {
 protected:
  BoolVarArray is_selected;  // is_selected[j]: medium j is bought
  IntVar total_cost;         // total cost of the selected media

 public:
  explicit MediaSelection(const json& instance) {
    std::vector<int> costs = instance.at("media_costs").get<std::vector<int>>();
    std::vector<std::vector<int>> incidence =
        instance.at("incidence_matrix").get<std::vector<std::vector<int>>>();
    int n_media = static_cast<int>(costs.size());
    int n_audiences = static_cast<int>(incidence.size());

    is_selected = BoolVarArray(*this, n_media, 0, 1);

    // every audience is reached by at least one selected medium
    // (audience i is reached by medium j when incidence[i][j] = 1)
    for (int i = 0; i < n_audiences; ++i) {
      BoolVarArgs reaching;
      for (int j = 0; j < n_media; ++j)
        if (incidence[i][j] == 1) reaching << is_selected[j];
      linear(*this, reaching, IRT_GQ, 1);
    }

    // total cost of the selected media is the campaign cost
    total_cost = expr(*this, sum(IntArgs(costs), is_selected));

    // the campaign should cost no more than necessary
    minimize(total_cost);

    // branch on the media decisions first; leave a medium out unless a cover needs it
    branch(*this, is_selected, BOOL_VAR_AFC_MAX(0.99), BOOL_VAL_MIN());
    restarts(100);

    output("is_selected", is_selected);
    output("min_total_cost", total_cost);
  }

  MediaSelection(MediaSelection& s) : dcp::Space(s) {
    is_selected.update(*this, s.is_selected);
    total_cost.update(*this, s.total_cost);
  }
  Gecode::Space* copy() override { return new MediaSelection(*this); }
};

DCP_MODEL(MediaSelection)
