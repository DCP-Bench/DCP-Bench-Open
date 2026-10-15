#include "dcp.h"

// Zebra puzzle (Einstein's puzzle): five houses in a row, each with a distinct
// colour, nationality, pet, drink and job. Find which house each item belongs to.
//
// Each of the five arrays maps an item to its house (0..4, left to right). The
// item indices follow the order of the description:
//   colours: yellow 0, green 1, red 2, white 3, blue 4
//   nations: italy 0, spain 1, japan 2, england 3, norway 4
//   pets:    cat 0, zebra 1, bear 2, snails 3, horse 4
//   drinks:  milk 0, water 1, tea 2, coffee 3, juice 4
//   jobs:    painter 0, sculptor 1, diplomat 2, pianist 3, doctor 4
// Two items of different kinds belong to the same inhabitant exactly when they
// are in the same house, so "X is Y" is an equality of house numbers.
class Zebra : public dcp::Space {
 protected:
  IntVarArray colors;   // colors[c]: house of colour c
  IntVarArray nations;  // nations[n]: house of nationality n
  IntVarArray pets;     // pets[p]: house of pet p
  IntVarArray drinks;   // drinks[d]: house of drink d
  IntVarArray jobs;     // jobs[j]: house of job j

  // Index constants (see the header comment).
  enum { YELLOW, GREEN, RED, WHITE, BLUE };
  enum { ITALY, SPAIN, JAPAN, ENGLAND, NORWAY };
  enum { CAT, ZEBRA, BEAR, SNAILS, HORSE };
  enum { MILK, WATER, TEA, COFFEE, JUICE };
  enum { PAINTER, SCULPTOR, DIPLOMAT, PIANIST, DOCTOR };

 public:
  // The instance file is empty: the puzzle is fixed and all data is in the description.
  explicit Zebra(const json& instance) {
    (void)instance;
    colors = IntVarArray(*this, 5, 0, 4);
    nations = IntVarArray(*this, 5, 0, 4);
    pets = IntVarArray(*this, 5, 0, 4);
    drinks = IntVarArray(*this, 5, 0, 4);
    jobs = IntVarArray(*this, 5, 0, 4);

    // five houses in a row, each painted a different colour
    distinct(*this, colors, IPL_DOM);
    // each inhabitant has a different nationality
    distinct(*this, nations, IPL_DOM);
    // each inhabitant owns a different pet
    distinct(*this, pets, IPL_DOM);
    // each inhabitant drinks a different beverage
    distinct(*this, drinks, IPL_DOM);
    // each inhabitant has a different job
    distinct(*this, jobs, IPL_DOM);

    // the painter owns the horse
    rel(*this, jobs[PAINTER] == pets[HORSE]);
    // the diplomat drinks coffee
    rel(*this, jobs[DIPLOMAT] == drinks[COFFEE]);
    // the one who drinks milk lives in the white house
    rel(*this, drinks[MILK] == colors[WHITE]);
    // the Spaniard is a painter
    rel(*this, nations[SPAIN] == jobs[PAINTER]);
    // the Englishman lives in the red house
    rel(*this, nations[ENGLAND] == colors[RED]);
    // the snails are owned by the sculptor
    rel(*this, pets[SNAILS] == jobs[SCULPTOR]);
    // the green house is immediately on the left of the red one
    rel(*this, colors[RED] == colors[GREEN] + 1);
    // the Norwegian lives immediately on the right of the blue house
    rel(*this, nations[NORWAY] == colors[BLUE] + 1);
    // the doctor drinks milk
    rel(*this, jobs[DOCTOR] == drinks[MILK]);
    // the diplomat is Japanese
    rel(*this, jobs[DIPLOMAT] == nations[JAPAN]);
    // the Norwegian owns the zebra
    rel(*this, nations[NORWAY] == pets[ZEBRA]);
    // the green house is next to the white one
    rel(*this, abs(colors[GREEN] - colors[WHITE]) == 1);
    // the horse is owned by the neighbour of the diplomat
    rel(*this, abs(pets[HORSE] - jobs[DIPLOMAT]) == 1);
    // the Italian either lives in the red, white or green house
    IntVarArgs italian_houses;
    italian_houses << colors[RED] << colors[WHITE] << colors[GREEN];
    member(*this, italian_houses, nations[ITALY], IPL_DOM);

    // no objective: any house assignment that satisfies the clues is a solution
    branch(*this, colors, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    branch(*this, nations, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    branch(*this, pets, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    branch(*this, drinks, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    branch(*this, jobs, INT_VAR_SIZE_MIN(), INT_VAL_MIN());

    output("colors", colors);
    output("nations", nations);
    output("pets", pets);
    output("drinks", drinks);
    output("jobs", jobs);
  }

  Zebra(Zebra& s) : dcp::Space(s) {
    colors.update(*this, s.colors);
    nations.update(*this, s.nations);
    pets.update(*this, s.pets);
    drinks.update(*this, s.drinks);
    jobs.update(*this, s.jobs);
  }

  Gecode::Space* copy() override { return new Zebra(*this); }
};

DCP_MODEL(Zebra)
