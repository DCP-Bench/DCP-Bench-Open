#include "dcp.h"

// Crew scheduling: assign flight attendants to flights so that each flight is
// staffed with its required crew size and its required mix of stewards,
// hostesses and speakers of each language. Every attendant has two flights off
// after an attended flight.
class CrewScheduling : public dcp::Space {
 protected:
  int flights;          // number of flights
  int people;           // number of flight attendants
  BoolVarArray works;   // works[f * people + p] = 1 if attendant p is assigned to flight f

 public:
  explicit CrewScheduling(const json& instance) {
    auto attributes = instance.at("attributes").get<std::vector<std::vector<int>>>();
    auto required = instance.at("required_crew").get<std::vector<std::vector<int>>>();
    flights = static_cast<int>(required.size());
    people = static_cast<int>(attributes.size());
    works = BoolVarArray(*this, flights * people, 0, 1);

    // works(f, p) is the assignment of attendant p to flight f
    auto works_on = [&](int f, int p) { return works[f * people + p]; };

    // each flight is staffed by exactly its crew size
    for (int f = 0; f < flights; ++f) {
      BoolVarArgs crew;
      for (int p = 0; p < people; ++p) crew << works_on(f, p);
      linear(*this, crew, IRT_EQ, required[f][0]);
    }

    // each flight has enough stewards, hostesses and speakers of each language;
    // attribute column j matches requirement column j + 1
    for (int f = 0; f < flights; ++f) {
      for (int j = 0; j < 5; ++j) {
        BoolVarArgs qualified;
        for (int p = 0; p < people; ++p)
          if (attributes[p][j] == 1) qualified << works_on(f, p);
        linear(*this, qualified, IRT_GQ, required[f][j + 1]);
      }
    }

    // two flights off after an attended flight: within any three consecutive
    // flights an attendant works at most one (this covers every pair of flights
    // at distance one or two, and the windows are cut at the last flight)
    for (int p = 0; p < people; ++p) {
      for (int f = 0; f + 1 < flights; ++f) {
        BoolVarArgs window;
        for (int g = f; g < flights && g <= f + 2; ++g) window << works_on(g, p);
        linear(*this, window, IRT_LQ, 1);
      }
    }

    branch(*this, works, BOOL_VAR_NONE(), BOOL_VAL_MIN());

    std::vector<BoolVarArgs> crew_rows(flights);
    for (int f = 0; f < flights; ++f)
      for (int p = 0; p < people; ++p) crew_rows[f] << works_on(f, p);
    output("crew", crew_rows);
  }

  CrewScheduling(CrewScheduling& s) : dcp::Space(s), flights(s.flights), people(s.people) {
    works.update(*this, s.works);
  }
  Gecode::Space* copy() override { return new CrewScheduling(*this); }
};

DCP_MODEL(CrewScheduling)
