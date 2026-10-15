#include "dcp.h"

// Allergy puzzle: four friends (Debra, Janet, Hugh, Rick) each have a different
// surname (Baxter, Lemon, Malone, Fleet) and a different allergy (eggs, mold,
// nuts, ragweed). Find who has each food and who has each surname.
// Friends are numbered Debra = 0, Janet = 1, Hugh = 2, Rick = 3. The puzzle has
// no instance data: the friends, foods and clues are all fixed by the statement.
class Allergy : public dcp::Space {
 protected:
  IntVar eggs, mold, nuts, ragweed;        // friend allergic to each food
  IntVar baxter, lemon, malone, fleet;     // friend with each surname

 public:
  explicit Allergy(const json& /* instance */) {
    // friend numbers from the statement
    const int debra = 0, janet = 1, hugh = 2, rick = 3;

    eggs = IntVar(*this, 0, 3);
    mold = IntVar(*this, 0, 3);
    nuts = IntVar(*this, 0, 3);
    ragweed = IntVar(*this, 0, 3);
    baxter = IntVar(*this, 0, 3);
    lemon = IntVar(*this, 0, 3);
    malone = IntVar(*this, 0, 3);
    fleet = IntVar(*this, 0, 3);

    // each friend has a different allergy: the four foods are all different
    IntVarArgs foods;
    foods << eggs << mold << nuts << ragweed;
    distinct(*this, foods, IPL_DOM);

    // each friend has a different surname
    IntVarArgs surnames;
    surnames << baxter << lemon << malone << fleet;
    distinct(*this, surnames, IPL_DOM);

    // Rick is not allergic to mold
    rel(*this, mold, IRT_NQ, rick);

    // Baxter is allergic to eggs: the Baxter friend is the egg-allergic friend
    rel(*this, baxter, IRT_EQ, eggs);

    // Hugh is neither surnamed Lemon nor Fleet
    rel(*this, lemon, IRT_NQ, hugh);
    rel(*this, fleet, IRT_NQ, hugh);

    // Debra is allergic to ragweed
    rel(*this, ragweed, IRT_EQ, debra);

    // Janet (who isn't Lemon) is neither allergic to eggs nor to mold
    rel(*this, lemon, IRT_NQ, janet);
    rel(*this, eggs, IRT_NQ, janet);
    rel(*this, mold, IRT_NQ, janet);

    // branch on every friend-number variable
    IntVarArgs all;
    all << eggs << mold << nuts << ragweed << baxter << lemon << malone << fleet;
    branch(*this, all, INT_VAR_SIZE_MIN(), INT_VAL_MIN());

    output("eggs", eggs);
    output("mold", mold);
    output("nuts", nuts);
    output("ragweed", ragweed);
    output("baxter", baxter);
    output("lemon", lemon);
    output("malone", malone);
    output("fleet", fleet);
  }

  Allergy(Allergy& s) : dcp::Space(s) {
    eggs.update(*this, s.eggs);
    mold.update(*this, s.mold);
    nuts.update(*this, s.nuts);
    ragweed.update(*this, s.ragweed);
    baxter.update(*this, s.baxter);
    lemon.update(*this, s.lemon);
    malone.update(*this, s.malone);
    fleet.update(*this, s.fleet);
  }
  Gecode::Space* copy() override { return new Allergy(*this); }
};

DCP_MODEL(Allergy)
