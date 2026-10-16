#include "dcp.h"

// Appointment scheduling: assign each of n people to one of n interview slots so
// that every person is placed only in a slot where they are free, and every slot
// holds exactly one person. x[i][j] is true when person i is assigned slot j.
// m[i][j] = 1 means person i is free in slot j (instance data).
class AppointmentScheduling : public dcp::Space {
 protected:
  IntVarArray slot;  // slot[i]: the slot assigned to person i
  BoolVarArray x;    // x[i * n + j]: person i is assigned slot j (one-hot over j)

 public:
  explicit AppointmentScheduling(const json& instance) {
    const json& m = instance.at("m");
    int n = static_cast<int>(m.size());

    slot = IntVarArray(*this, n, 0, n - 1);
    x = BoolVarArray(*this, n * n, 0, 1);

    for (int i = 0; i < n; ++i) {
      // person i can only be placed in a slot where they are free
      IntArgs free_slots;
      for (int j = 0; j < n; ++j)
        if (m[i][j].get<int>() == 1) free_slots << j;
      if (free_slots.size() == 0) {
        // nobody is free in any slot: no schedule exists
        this->fail();
        return;
      }
      dom(*this, slot[i], IntSet(free_slots));

      // link the slot to the Boolean view: x[i][j] = 1 iff person i has slot j
      BoolVarArgs row;
      for (int j = 0; j < n; ++j) row << x[i * n + j];
      channel(*this, row, slot[i], 0);
    }

    // no two people share an interview slot
    distinct(*this, slot, IPL_DOM);

    // every slot holds exactly one person
    for (int j = 0; j < n; ++j) {
      BoolVarArgs column;
      for (int i = 0; i < n; ++i) column << x[i * n + j];
      linear(*this, column, IRT_EQ, 1);
    }

    branch(*this, slot, INT_VAR_SIZE_MIN(), INT_VAL_MIN());

    std::vector<BoolVarArgs> rows(n);
    for (int i = 0; i < n; ++i)
      for (int j = 0; j < n; ++j) rows[i] << x[i * n + j];
    output("x", rows);
  }

  AppointmentScheduling(AppointmentScheduling& s) : dcp::Space(s) {
    slot.update(*this, s.slot);
    x.update(*this, s.x);
  }
  Gecode::Space* copy() override { return new AppointmentScheduling(*this); }
};

DCP_MODEL(AppointmentScheduling)
