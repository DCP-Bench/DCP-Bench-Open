#include "dcp.h"

// Room assignment: assign each request to one of max_rooms rooms so that every
// request gets one room for its whole stay, a few requests keep a pre-assigned
// room, and no room serves two requests at the same time.
// A request occupies the nights from its start date up to, not including, its
// end date (the end date is exclusive).

namespace {

// Day number (days since 1970-01-01) of a date given as "YYYY-MM-DD".
int day_number(const std::string& date) {
  int y = std::stoi(date.substr(0, 4));
  unsigned m = static_cast<unsigned>(std::stoi(date.substr(5, 2)));
  unsigned d = static_cast<unsigned>(std::stoi(date.substr(8, 2)));
  // Howard Hinnant's days_from_civil algorithm.
  y -= m <= 2;
  const int era = (y >= 0 ? y : y - 399) / 400;
  const unsigned yoe = static_cast<unsigned>(y - era * 400);
  const unsigned doy = (153 * (m > 2 ? m - 3 : m + 9) + 2) / 5 + d - 1;
  const unsigned doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
  return era * 146097 + static_cast<int>(doe) - 719468;
}

}  // namespace

class RoomAssignment : public dcp::Space {
 protected:
  IntVarArray room;  // room[i]: room of request i

 public:
  explicit RoomAssignment(const json& instance) {
    int max_rooms = instance.at("max_rooms").get<int>();
    std::vector<std::string> start_data = instance.at("start_data").get<std::vector<std::string>>();
    std::vector<std::string> end_data = instance.at("end_data").get<std::vector<std::string>>();
    std::vector<int> preassigned = instance.at("preassigned_room_data").get<std::vector<int>>();
    int n = static_cast<int>(start_data.size());

    std::vector<int> start(n), end(n);
    for (int i = 0; i < n; ++i) {
      start[i] = day_number(start_data[i]);
      end[i] = day_number(end_data[i]);
    }

    // each request is assigned to one room
    room = IntVarArray(*this, n, 0, max_rooms - 1);

    // some requests already have a room
    for (int i = 0; i < n; ++i)
      if (preassigned[i] >= 0) rel(*this, room[i], IRT_EQ, preassigned[i]);

    // a room serves one request at a time: requests staying on the same day
    // must have different rooms. Each start day gives the requests active on it.
    std::vector<int> start_days(start);
    std::sort(start_days.begin(), start_days.end());
    start_days.erase(std::unique(start_days.begin(), start_days.end()), start_days.end());
    for (int day : start_days) {
      IntVarArgs active;
      for (int i = 0; i < n; ++i)
        if (start[i] <= day && day < end[i]) active << room[i];
      if (active.size() >= 2) distinct(*this, active, IPL_DOM);
    }

    branch(*this, room, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    output("room_assignments", room);
  }

  RoomAssignment(RoomAssignment& s) : dcp::Space(s) {
    room.update(*this, s.room);
  }
  Gecode::Space* copy() override { return new RoomAssignment(*this); }
};

DCP_MODEL(RoomAssignment)
