#include "dcp.h"

// Car selection: assign participants to cars so that each participant gets at most
// one car and each car goes to at most one participant. A participant can only get
// a car they are interested in. Maximise the total number of assignments.
class CarSelection : public dcp::Space {
 protected:
  BoolVarArray a;   // a[i*m + j] = 1 if participant i is assigned to car j
  IntVar total;     // total number of assignments

 public:
  explicit CarSelection(const json& instance) {
    const auto& possible = instance.at("possible_assignments");
    int n = static_cast<int>(possible.size());         // participants (from the instance)
    int m = static_cast<int>(possible[0].size());      // cars (from the instance)

    a = BoolVarArray(*this, n * m, 0, 1);

    // each participant is assigned to at most one car
    for (int i = 0; i < n; ++i) {
      BoolVarArgs row;
      for (int j = 0; j < m; ++j) row << a[i * m + j];
      linear(*this, row, IRT_LQ, 1);
    }

    // each car is assigned to at most one participant
    for (int j = 0; j < m; ++j) {
      BoolVarArgs col;
      for (int i = 0; i < n; ++i) col << a[i * m + j];
      linear(*this, col, IRT_LQ, 1);
    }

    // a participant is only assigned to a car they are interested in
    for (int i = 0; i < n; ++i)
      for (int j = 0; j < m; ++j)
        if (possible[i][j].get<int>() == 0) rel(*this, a[i * m + j], IRT_EQ, 0);

    // the objective: total number of assignments
    BoolVarArgs all;
    for (int k = 0; k < n * m; ++k) all << a[k];
    total = expr(*this, sum(all));

    branch(*this, a, BOOL_VAR_NONE(), BOOL_VAL_MAX());
    maximize(total);

    std::vector<BoolVarArgs> rows;
    for (int i = 0; i < n; ++i) {
      BoolVarArgs row;
      for (int j = 0; j < m; ++j) row << a[i * m + j];
      rows.push_back(row);
    }
    output("assignments", rows);
  }

  CarSelection(CarSelection& s) : dcp::Space(s) {
    a.update(*this, s.a);
    total.update(*this, s.total);
  }
  Gecode::Space* copy() override { return new CarSelection(*this); }
};

DCP_MODEL(CarSelection)
