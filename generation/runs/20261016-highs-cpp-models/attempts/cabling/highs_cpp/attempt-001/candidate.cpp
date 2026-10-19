// Place the devices of a rack in a line so that the sum of all cable lengths is as short as possible.
#include "dcp.h"

#include <string>
#include <vector>

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  const int n = instance.at("n").get<int>();
  const json& devices = instance.at("devices");

  // y[d][k] = 1 when device d is placed in rack position k (positions 0..n-1)
  std::vector<std::vector<dcp::Lin>> y(n, std::vector<dcp::Lin>(n));
  for (int d = 0; d < n; ++d)
    for (int k = 0; k < n; ++k) y[d][k] = dcp::new_var(h, 0, 1);

  // every device takes exactly one position
  for (int d = 0; d < n; ++d) {
    dcp::Lin one_position;
    for (int k = 0; k < n; ++k) one_position = one_position + y[d][k];
    dcp::add_row(h, one_position, 1, 1);
  }

  // every position holds exactly one device
  for (int k = 0; k < n; ++k) {
    dcp::Lin one_device;
    for (int d = 0; d < n; ++d) one_device = one_device + y[d][k];
    dcp::add_row(h, one_device, 1, 1);
  }

  // pos[d] is the rack position of device d
  std::vector<dcp::Lin> pos(n);
  for (int d = 0; d < n; ++d)
    for (int k = 0; k < n; ++k) pos[d] = pos[d] + static_cast<double>(k) * y[d][k];

  // the device name in the instance maps to its index in the devices list
  auto index_of = [&](const std::string& name) {
    for (std::size_t i = 0; i < devices.size(); ++i)
      if (devices[i].get<std::string>() == name) return static_cast<int>(i);
    throw std::runtime_error("unknown device " + name);
  };

  // each cable between two devices is as long as the distance between their positions;
  // the length variable z is at least that distance, and minimising pushes it to the distance
  dcp::Lin total;
  for (const json& cable : instance.at("cable_struct")) {
    int a = index_of(cable.at(0).get<std::string>());
    int b = index_of(cable.at(1).get<std::string>());
    int count = cable.at(2).get<int>();
    dcp::Lin length = dcp::new_var(h, 0, n - 1);
    // length >= pos[a] - pos[b]
    dcp::add_row(h, length - (pos[a] - pos[b]), 0, kHighsInf);
    // length >= pos[b] - pos[a]
    dcp::add_row(h, length - (pos[b] - pos[a]), 0, kHighsInf);
    // the sum of all cable lengths: each cable of this pair adds its length
    total = total + static_cast<double>(count) * length;
  }

  // the sum of all cable lengths is minimised, and it is the output final_sum
  out.minimize(total);
  out.add("final_sum", total);
}
