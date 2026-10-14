#include "dcp.h"

// Shoe shopping order: Harriet bought four pairs of shoes (ecru espadrilles,
// fuchsia flats, purple pumps, suede sandals) at four stores (Foot Farm, Heels in
// a Handcart, The Shoe Palace, Tootsies), one pair per stop. Find the stop
// number (1 to 4) of each shoe and of each store.
class ArchFriends : public dcp::Space {
 protected:
  IntVar ecru, fuchsia, purple, suede;       // stop number of each shoe
  IntVar foot, heels, palace, tootsies;      // stop number of each store

 public:
  explicit ArchFriends(const json& instance) {
    (void)instance;  // the puzzle has no instance data; all values come from the description
    ecru = IntVar(*this, 1, 4);
    fuchsia = IntVar(*this, 1, 4);
    purple = IntVar(*this, 1, 4);
    suede = IntVar(*this, 1, 4);
    foot = IntVar(*this, 1, 4);
    heels = IntVar(*this, 1, 4);
    palace = IntVar(*this, 1, 4);
    tootsies = IntVar(*this, 1, 4);

    // each of the four shoes is bought at a different stop
    IntVarArgs shoes;
    shoes << ecru << fuchsia << purple << suede;
    distinct(*this, shoes, IPL_DOM);

    // each of the four stores is a different stop
    IntVarArgs stores;
    stores << foot << heels << palace << tootsies;
    distinct(*this, stores, IPL_DOM);

    // the fuchsia flats were bought at Heels in a Handcart (same stop)
    rel(*this, heels == fuchsia);

    // the store visited just after the purple pumps was not Tootsies
    // (vacuously true when the purple pumps were the last stop)
    rel(*this, tootsies != purple + 1);

    // The Foot Farm was Harriet's second stop
    rel(*this, foot == 2);

    // two stops after leaving The Shoe Palace, Harriet bought the suede sandals
    rel(*this, suede == palace + 2);

    branch(*this, shoes, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    branch(*this, stores, INT_VAR_SIZE_MIN(), INT_VAL_MIN());

    output("ecruespadrilles", ecru);
    output("fuchsiaflats", fuchsia);
    output("purplepumps", purple);
    output("suedesandals", suede);
    output("footfarm", foot);
    output("heelsinahandcart", heels);
    output("theshoepalace", palace);
    output("tootsies", tootsies);
  }

  ArchFriends(ArchFriends& s) : dcp::Space(s) {
    ecru.update(*this, s.ecru);
    fuchsia.update(*this, s.fuchsia);
    purple.update(*this, s.purple);
    suede.update(*this, s.suede);
    foot.update(*this, s.foot);
    heels.update(*this, s.heels);
    palace.update(*this, s.palace);
    tootsies.update(*this, s.tootsies);
  }
  Gecode::Space* copy() override { return new ArchFriends(*this); }
};

DCP_MODEL(ArchFriends)
