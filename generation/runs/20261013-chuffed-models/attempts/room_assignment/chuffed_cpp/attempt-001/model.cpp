// Room assignment: give each request one room for its whole stay, so that a room serves
// one request at a time; some requests already have a room fixed.
#include "dcp.h"

#include <cstdio>
#include <string>
#include <vector>

// day number of a date "YYYY-MM-DD" (days since 1970-01-01, proleptic Gregorian calendar)
static int day_number(const std::string& date) {
  int y = 0, m = 0, d = 0;
  std::sscanf(date.c_str(), "%d-%d-%d", &y, &m, &d);
  y -= m <= 2;
  int era = (y >= 0 ? y : y - 399) / 400;
  int yoe = y - era * 400;
  int doy = (153 * (m + (m > 2 ? -3 : 9)) + 2) / 5 + d - 1;
  int doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
  return era * 146097 + doe - 719468;
}

void Build(const json& instance, json& outputs) {
  int max_rooms = instance.at("max_rooms");
  std::vector<std::string> start_data = instance.at("start_data").get<std::vector<std::string>>();
  std::vector<std::string> end_data = instance.at("end_data").get<std::vector<std::string>>();
  std::vector<int> preassigned = instance.at("preassigned_room_data").get<std::vector<int>>();
  int n = static_cast<int>(start_data.size());

  // start[i] and end[i] are the check-in and check-out day numbers of request i; the end
  // day is exclusive, so a request ending on a day does not block one starting that day
  std::vector<int> start(n), end(n);
  for (int i = 0; i < n; ++i) {
    start[i] = day_number(start_data[i]);
    end[i] = day_number(end_data[i]);
  }

  // room[i] is the room that serves request i
  vec<IntVar*> room;
  createVars(room, n, 0, max_rooms - 1);

  // a request with a pre-assigned room (not -1) is in that room
  for (int i = 0; i < n; ++i) {
    if (preassigned[i] >= 0) int_rel(room[i], IRT_EQ, preassigned[i]);
  }

  // two requests whose stays overlap cannot share a room
  for (int i = 0; i < n; ++i) {
    for (int j = i + 1; j < n; ++j) {
      bool overlap = start[i] < end[j] && start[j] < end[i];
      if (overlap) int_rel(room[i], IRT_NE, room[j]);
    }
  }

  // branch on the requests in order, lowest room first
  branch(room, VAR_INORDER, VAL_MIN);

  json assignments = json::array();
  for (int i = 0; i < n; ++i) assignments.push_back(dcp::out(room[i]));
  outputs = {{"room_assignments", assignments}};
}
