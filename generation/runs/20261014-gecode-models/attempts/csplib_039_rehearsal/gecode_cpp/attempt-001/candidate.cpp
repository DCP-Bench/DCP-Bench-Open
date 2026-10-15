#include "dcp.h"

// Rehearsal order: pieces of music are rehearsed one after another in some order.
// Each player arrives before the first piece they play and leaves after the last one,
// so the time they are waiting is the time they are present minus the time they play.
// Minimise the total waiting time of all players.
class Rehearsal : public dcp::Space {
 protected:
  IntVarArray order;       // order[k]: piece rehearsed in the k-th slot
  IntVarArray pos;         // pos[p]: slot in which piece p is rehearsed
  IntVarArray slot_start;  // slot_start[k]: time at which slot k begins
  IntVarArray start;       // start[p]: time at which piece p begins
  IntVar total;            // total waiting time of all players

 public:
  explicit Rehearsal(const json& instance) {
    int n = instance.at("num_pieces").get<int>();
    std::vector<int> duration = instance.at("duration").get<std::vector<int>>();
    std::vector<std::vector<int>> rehearsal =
        instance.at("rehearsal").get<std::vector<std::vector<int>>>();  // rehearsal[j][p]: player j plays piece p
    int m = static_cast<int>(rehearsal.size());

    int horizon = 0;  // the sum of all durations: no slot starts after it
    for (int d : duration) horizon += d;

    order = IntVarArray(*this, n, 0, n - 1);
    pos = IntVarArray(*this, n, 0, n - 1);
    slot_start = IntVarArray(*this, n, 0, horizon);
    start = IntVarArray(*this, n, 0, horizon);

    // every piece is rehearsed in exactly one slot, and every slot holds one piece
    distinct(*this, order, IPL_DOM);
    channel(*this, order, pos, IPL_DOM);

    // the first slot begins at time 0
    rel(*this, slot_start[0] == 0);

    // a slot begins when the previous slot's piece has finished
    for (int k = 0; k + 1 < n; ++k) {
      IntVar d = expr(*this, element(IntArgs(duration), order[k]));
      rel(*this, slot_start[k + 1] == slot_start[k] + d);
    }

    // a piece begins when its slot begins
    for (int p = 0; p < n; ++p) {
      IntVarArgs slots;
      for (int k = 0; k < n; ++k) slots << slot_start[k];
      element(*this, slots, pos[p], start[p]);
    }

    // a player is present from the start of the first piece they play until the end of the last
    IntVarArgs firsts, lasts;
    int played = 0;  // total time players spend playing, summed over players
    for (int j = 0; j < m; ++j) {
      IntVarArgs begins, ends;
      for (int p = 0; p < n; ++p) {
        if (rehearsal[j][p] != 1) continue;
        begins << start[p];
        ends << expr(*this, start[p] + duration[p]);
        played += duration[p];
      }
      if (begins.size() == 0) continue;  // a player in no piece is never present
      IntVar first(*this, 0, horizon);
      IntVar last(*this, 0, horizon);
      min(*this, begins, first, IPL_DEF);
      max(*this, ends, last, IPL_DEF);
      firsts << first;
      lasts << last;
    }

    // waiting time = presence - playing, summed over all players
    total = expr(*this, sum(lasts) - sum(firsts) - played);

    branch(*this, order, INT_VAR_NONE(), INT_VAL_MIN());
    branch(*this, slot_start, INT_VAR_NONE(), INT_VAL_MIN());
    branch(*this, start, INT_VAR_NONE(), INT_VAL_MIN());
    output("rehearsal_order", order);
    minimize(total);
  }

  Rehearsal(Rehearsal& s) : dcp::Space(s) {
    order.update(*this, s.order);
    pos.update(*this, s.pos);
    slot_start.update(*this, s.slot_start);
    start.update(*this, s.start);
    total.update(*this, s.total);
  }
  Gecode::Space* copy() override { return new Rehearsal(*this); }
};

DCP_MODEL(Rehearsal)
