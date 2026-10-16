// CSPLib 016 traffic lights: a four-way junction with eight traffic lights. Four lights
// V1..V4 are for vehicles (0=red, 1=red-yellow, 2=green, 3=yellow) and four lights P1..P4
// are for pedestrians (0=red, 1=green). For i=1..4 (with V5=V1 and P5=P1), the combination
// (V_i, P_i, V_i+1, P_i+1) must be one of the allowed tuples; every other combination is
// disallowed. Output lights = [V1, V2, V3, V4, P1, P2, P3, P4].
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  // the allowed (V_i, P_i, V_i+1, P_i+1) combinations, as given by the instance
  const json& allowed = instance.at("allowed_tuples");
  const size_t count = allowed.size();

  // vehicle light states 0..3 and pedestrian light states 0..1
  std::vector<dcp::Lin> V, P;
  for (int i = 0; i < 4; ++i) V.push_back(dcp::new_var(h, 0, 3));
  for (int i = 0; i < 4; ++i) P.push_back(dcp::new_var(h, 0, 1));

  // for each i, the lights (V_i, P_i, V_i+1, P_i+1) take exactly one of the allowed tuples
  for (int i = 0; i < 4; ++i) {
    const int j = (i + 1) % 4;  // the next light, wrapping from light 4 to light 1

    // selector b[k] = 1 picks allowed tuple k for this pair; exactly one tuple is picked
    std::vector<dcp::Lin> b;
    dcp::Lin picked;
    for (size_t k = 0; k < count; ++k) {
      b.push_back(dcp::new_var(h, 0, 1));
      picked = picked + b[k];
    }
    // exactly one allowed tuple is chosen for this pair
    dcp::add_row(h, picked, 1, 1);

    // the value of each light is the value in the chosen tuple
    dcp::Lin v_i, p_i, v_j, p_j;
    for (size_t k = 0; k < count; ++k) {
      v_i = v_i + static_cast<double>(allowed[k][0].get<int>()) * b[k];
      p_i = p_i + static_cast<double>(allowed[k][1].get<int>()) * b[k];
      v_j = v_j + static_cast<double>(allowed[k][2].get<int>()) * b[k];
      p_j = p_j + static_cast<double>(allowed[k][3].get<int>()) * b[k];
    }
    // vehicle light i takes its value from the chosen tuple
    dcp::add_row(h, V[i] - v_i, 0, 0);
    // pedestrian light i takes its value from the chosen tuple
    dcp::add_row(h, P[i] - p_i, 0, 0);
    // vehicle light i+1 takes its value from the chosen tuple
    dcp::add_row(h, V[j] - v_j, 0, 0);
    // pedestrian light i+1 takes its value from the chosen tuple
    dcp::add_row(h, P[j] - p_j, 0, 0);
  }

  // the printed answer: [V1, V2, V3, V4, P1, P2, P3, P4]
  std::vector<dcp::Lin> lights;
  for (const auto& v : V) lights.push_back(v);
  for (const auto& p : P) lights.push_back(p);
  out.add("lights", lights);
}
