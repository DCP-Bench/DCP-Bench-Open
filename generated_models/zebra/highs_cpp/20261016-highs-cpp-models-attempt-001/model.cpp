// Zebra puzzle (Einstein's puzzle): five houses in a row, numbered 0 to 4 from left to right.
// Each house has one colour, one nationality, one pet, one drink and one job, and every
// value of each category is used once. Output: the house of each colour, nationality,
// job, pet and drink, in the order the description lists them.
#include "dcp.h"

namespace {

const int HOUSES = 5;  // five houses, from the description

// Item numbering: 5 categories of 5 values, item = base + value.
const int COLOR = 0, NATION = 5, PET = 10, DRINK = 15, JOB = 20;

// Item indices by name, as in the description's lists.
enum : int {
  YELLOW = COLOR + 0, GREEN = COLOR + 1, RED = COLOR + 2, WHITE = COLOR + 3, BLUE = COLOR + 4,
  ITALY = NATION + 0, SPAIN = NATION + 1, JAPAN = NATION + 2, ENGLAND = NATION + 3, NORWAY = NATION + 4,
  CAT = PET + 0, ZEBRA = PET + 1, BEAR = PET + 2, SNAILS = PET + 3, HORSE = PET + 4,
  MILK = DRINK + 0, WATER = DRINK + 1, TEA = DRINK + 2, COFFEE = DRINK + 3, JUICE = DRINK + 4,
  PAINTER = JOB + 0, SCULPTOR = JOB + 1, DIPLOMAT = JOB + 2, PIANIST = JOB + 3, DOCTOR = JOB + 4,
};

using dcp::Lin;

// Adds a binary column and returns it.
Lin binary(Highs& h) { return dcp::new_var(h, 0, 1, true); }

// House of an item: the house index weighted by the item's house indicator.
Lin house_of(const std::vector<std::vector<Lin>>& b, int item) {
  Lin e;
  for (int house = 0; house < HOUSES; ++house) e = e + static_cast<double>(house) * b[item][house];
  return e;
}

// Two items share a house: house_of(a) = house_of(b).
void same_house(Highs& h, const std::vector<std::vector<Lin>>& b, int a, int c) {
  dcp::add_row(h, house_of(b, a) - house_of(b, c), 0, 0);
}

// Item a is in the house immediately right of item c: house_of(a) = house_of(c) + 1.
void right_of(Highs& h, const std::vector<std::vector<Lin>>& b, int a, int c) {
  dcp::add_row(h, house_of(b, a) - house_of(b, c), 1, 1);
}

// Items a and c are in adjacent houses (either order), with binary s:
// s = 1 gives house(a) = house(c) + 1, s = 0 gives house(c) = house(a) + 1.
// Big-M = 5: house differences lie in -4..4, so a difference of 1 is at most 5 away.
void next_to(Highs& h, const std::vector<std::vector<Lin>>& b, int a, int c) {
  Lin s = binary(h);
  Lin d = house_of(b, a) - house_of(b, c);
  dcp::add_row(h, d - 5.0 * s, -4, kHighsInf);     // s = 1: d >= 1
  dcp::add_row(h, d + 5.0 * s, -kHighsInf, 6);     // s = 1: d <= 1
  dcp::add_row(h, d + 5.0 * s, -1, kHighsInf);     // s = 0: d >= -1
  dcp::add_row(h, d - 5.0 * s, -kHighsInf, -1);    // s = 0: d <= -1
}

}  // namespace

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  (void)instance;  // the puzzle is fixed: five houses, no instance data
  const int items = 25;

  // b[item][house] = 1 when the item is in that house.
  std::vector<std::vector<Lin>> b(items, std::vector<Lin>(HOUSES));
  for (int item = 0; item < items; ++item)
    for (int house = 0; house < HOUSES; ++house) b[item][house] = binary(h);

  // Each item is in exactly one house.
  for (int item = 0; item < items; ++item) {
    Lin all;
    for (int house = 0; house < HOUSES; ++house) all = all + b[item][house];
    dcp::add_row(h, all, 1, 1);
  }

  // Each house has exactly one item from each category.
  for (int base : {COLOR, NATION, PET, DRINK, JOB}) {
    for (int house = 0; house < HOUSES; ++house) {
      Lin one;
      for (int v = 0; v < HOUSES; ++v) one = one + b[base + v][house];
      dcp::add_row(h, one, 1, 1);
    }
  }

  // the painter owns the horse
  same_house(h, b, PAINTER, HORSE);
  // the diplomat drinks coffee
  same_house(h, b, DIPLOMAT, COFFEE);
  // the one who drinks milk lives in the white house
  same_house(h, b, MILK, WHITE);
  // the Spaniard is a painter
  same_house(h, b, SPAIN, PAINTER);
  // the Englishman lives in the red house
  same_house(h, b, ENGLAND, RED);
  // the snails are owned by the sculptor
  same_house(h, b, SNAILS, SCULPTOR);
  // the green house is immediately on the left of the red one
  right_of(h, b, RED, GREEN);
  // the Norwegian lives immediately on the right of the blue house
  right_of(h, b, NORWAY, BLUE);
  // the doctor drinks milk
  same_house(h, b, DOCTOR, MILK);
  // the diplomat is Japanese
  same_house(h, b, DIPLOMAT, JAPAN);
  // the Norwegian owns the zebra
  same_house(h, b, NORWAY, ZEBRA);
  // the green house is next to the white one
  next_to(h, b, GREEN, WHITE);
  // the horse is owned by the neighbour of the diplomat
  next_to(h, b, HORSE, DIPLOMAT);
  // the Italian either lives in the red, white or green house
  for (int house = 0; house < HOUSES; ++house)
    dcp::add_row(h, b[ITALY][house] - b[RED][house] - b[WHITE][house] - b[GREEN][house], -kHighsInf, 0);

  auto houses_of = [&](int base) {
    std::vector<Lin> v;
    for (int k = 0; k < HOUSES; ++k) v.push_back(house_of(b, base + k));
    return v;
  };
  out.add("colors", houses_of(COLOR));
  out.add("nations", houses_of(NATION));
  out.add("pets", houses_of(PET));
  out.add("drinks", houses_of(DRINK));
  out.add("jobs", houses_of(JOB));
}
