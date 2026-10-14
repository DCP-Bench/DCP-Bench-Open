#include "dcp.h"

// Traffic lights at a four-way junction: eight lights, four for vehicles (V1..V4)
// and four for pedestrians (P1..P4). Find a valid assignment of light states
// lights = [V1, V2, V3, V4, P1, P2, P3, P4] where each pair of neighbouring
// roads (V_i, P_i, V_i+1, P_i+1) for i = 1..4 (cyclic, V5 = V1, P5 = P1) is a
// safe combination.
class TrafficLights : public dcp::Space {
 protected:
  IntVarArray lights;  // lights[0..3] = V1..V4, lights[4..7] = P1..P4

 public:
  explicit TrafficLights(const json& instance) : lights(*this, 8, 0, 3) {
    // vehicle states: 0=red, 1=red-yellow, 2=green, 3=yellow
    // pedestrian states: 0=red, 1=green
    for (int i = 4; i < 8; ++i) rel(*this, lights[i] <= 1);

    // safe combinations of the instance, read as (V_i, P_i, V_i+1, P_i+1)
    const json& allowed = instance.at("allowed_tuples");
    TupleSet safe(4);
    for (const auto& t : allowed) {
      IntArgs tuple(4);
      for (int k = 0; k < 4; ++k) tuple[k] = t[k].get<int>();
      safe.add(tuple);
    }
    safe.finalize();

    // for each junction i: the pair of vehicle and pedestrian states must be safe
    // with the next junction, wrapping around from light 4 to light 1
    for (int i = 0; i < 4; ++i) {
      int vi = i, pi = 4 + i;
      int vn = (i + 1) % 4, pn = 4 + (i + 1) % 4;
      IntVarArgs x;
      x << lights[vi] << lights[pi] << lights[vn] << lights[pn];
      // every other combination is disallowed
      extensional(*this, x, safe);
    }

    branch(*this, lights, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    output("lights", lights);
  }

  TrafficLights(TrafficLights& s) : dcp::Space(s) { lights.update(*this, s.lights); }
  Gecode::Space* copy() override { return new TrafficLights(*this); }
};

DCP_MODEL(TrafficLights)
