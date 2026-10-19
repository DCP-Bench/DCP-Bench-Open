// Row seating (minimise): seat n guests in a row of n chairs so that no two enemies
// sit side by side, and minimise the total distance from each guest's preferred chair.
#include <gecode/int.hh>
#include <gecode/minimodel.hh>
#include <gecode/search.hh>
#include <iostream>
#include <utility>
#include <vector>
using namespace Gecode;

const std::vector<int> kPreferred = {0, 0, 1, 2, 5, 5};
const std::vector<std::pair<int, int>> kEnemies = {{0, 1}, {1, 2}, {2, 3}, {4, 5}, {0, 3}};

class Seating : public IntMinimizeSpace {
 protected:
  IntVarArray seat;   // seat[g]: chair of guest g
  IntVarArray guest;  // guest[c]: guest on chair c
  IntVar total;

 public:
  Seating() {
    int n = kPreferred.size();
    seat = IntVarArray(*this, n, 0, n - 1);
    guest = IntVarArray(*this, n, 0, n - 1);

    // every chair holds exactly one guest (seat and guest are inverse permutations)
    channel(*this, seat, guest, IPL_DOM);

    // enemies never sit side by side
    for (auto [a, b] : kEnemies) rel(*this, abs(seat[a] - seat[b]) >= 2);

    // minimise the total distance from the preferred chairs
    IntVarArgs distance;
    for (int g = 0; g < n; ++g) distance << expr(*this, abs(seat[g] - kPreferred[g]));
    total = expr(*this, sum(distance));

    branch(*this, seat, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
  }
  Seating(Seating& s) : IntMinimizeSpace(s) {
    seat.update(*this, s.seat);
    guest.update(*this, s.guest);
    total.update(*this, s.total);
  }
  Space* copy() override { return new Seating(*this); }
  IntVar cost() const override { return total; }
  void print() const {
    std::cout << "Total distance: " << total.val() << "\nChairs:";
    for (int c = 0; c < guest.size(); ++c) std::cout << " " << guest[c].val();
    std::cout << "\n";
  }
};

int main() {
  Seating* root = new Seating;
  BAB<Seating> engine(root);
  delete root;
  Seating* best = nullptr;
  while (Seating* s = engine.next()) {  // each solution strictly improves the last
    delete best;
    best = s;
  }
  if (best == nullptr) {
    std::cout << (engine.stopped() ? "Stopped, no seating found" : "No valid seating") << "\n";
    return 0;
  }
  best->print();
  if (engine.stopped()) std::cout << "(not proven optimal)\n";
  delete best;
  return 0;
}
