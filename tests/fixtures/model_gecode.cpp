#include "dcp.h"

class Model : public dcp::Space {
  IntVarArray v;
 public:
  explicit Model(const json& instance) : v(*this, 2, 0, instance.at("n").get<int>()) {
    int n = instance.at("n");
    IntVarArgs xy(2);
    xy[0] = v[0];
    xy[1] = v[1];
    if (instance.at("optimize").get<bool>()) {
      linear(*this, xy, IRT_GQ, n);
      IntVar total(*this, 0, 2 * n);
      IntVarArgs all(3);
      all[0] = v[0];
      all[1] = v[1];
      all[2] = total;
      linear(*this, IntArgs({1, 1, -1}), all, IRT_EQ, 0);
      minimize(total);
    } else {
      linear(*this, xy, IRT_EQ, n);
    }
    branch(*this, v, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    output("x", v[0]);
    output("y", v[1]);
  }
  Model(Model& s) : dcp::Space(s) { v.update(*this, s.v); }
  Gecode::Space* copy() override { return new Model(*this); }
};
DCP_MODEL(Model)
