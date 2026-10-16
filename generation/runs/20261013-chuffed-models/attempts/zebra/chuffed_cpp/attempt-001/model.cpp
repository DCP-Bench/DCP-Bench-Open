// Zebra puzzle: five houses in a row; find the house (0..4) of each color, nationality, job, pet and drink.
#include "dcp.h"

// helper: five variables with different house numbers 0..4
static void HouseVars(vec<IntVar*>& v) {
  createVars(v, 5, 0, 4, true);
  all_different(v);
}

void Build(const json& instance, json& outputs) {
  // the order of the names below is the order of the declared outputs
  // colors: yellow, green, red, white, blue
  vec<IntVar*> colors;
  HouseVars(colors);
  IntVar *yellow = colors[0], *green = colors[1], *red = colors[2], *white = colors[3], *blue = colors[4];
  (void)yellow;
  // nations: italy, spain, japan, england, norway
  vec<IntVar*> nations;
  HouseVars(nations);
  IntVar *italy = nations[0], *spain = nations[1], *japan = nations[2], *england = nations[3], *norway = nations[4];
  // pets: cat, zebra, bear, snails, horse
  vec<IntVar*> pets;
  HouseVars(pets);
  IntVar *zebra = pets[1], *snails = pets[3], *horse = pets[4];
  // drinks: milk, water, tea, coffee, juice
  vec<IntVar*> drinks;
  HouseVars(drinks);
  IntVar *milk = drinks[0], *coffee = drinks[3];
  // jobs: painter, sculptor, diplomat, pianist, doctor
  vec<IntVar*> jobs;
  HouseVars(jobs);
  IntVar *painter = jobs[0], *sculptor = jobs[1], *diplomat = jobs[2], *doctor = jobs[4];

  // the painter owns the horse
  int_rel(painter, IRT_EQ, horse);
  // the diplomat drinks coffee
  int_rel(diplomat, IRT_EQ, coffee);
  // the one who drinks milk lives in the white house
  int_rel(milk, IRT_EQ, white);
  // the Spaniard is a painter
  int_rel(spain, IRT_EQ, painter);
  // the Englishman lives in the red house
  int_rel(england, IRT_EQ, red);
  // the snails are owned by the sculptor
  int_rel(snails, IRT_EQ, sculptor);
  // the green house is immediately on the left of the red one
  int_rel(green, IRT_EQ, red, -1);
  // the Norwegian lives immediately on the right of the blue house
  int_rel(norway, IRT_EQ, blue, 1);
  // the doctor drinks milk
  int_rel(doctor, IRT_EQ, milk);
  // the diplomat is Japanese
  int_rel(diplomat, IRT_EQ, japan);
  // the Norwegian owns the zebra
  int_rel(norway, IRT_EQ, zebra);

  // the green house is next to the white one: |green - white| = 1
  IntVar* gw = newIntVar(-4, 4);
  int_minus(green, white, gw);
  IntVar* gw_abs = newIntVar(0, 4);
  int_abs(gw, gw_abs);
  int_rel(gw_abs, IRT_EQ, 1);

  // the horse is owned by the neighbor of the diplomat: |horse - diplomat| = 1
  IntVar* hd = newIntVar(-4, 4);
  int_minus(horse, diplomat, hd);
  IntVar* hd_abs = newIntVar(0, 4);
  int_abs(hd, hd_abs);
  int_rel(hd_abs, IRT_EQ, 1);

  // the Italian lives in the red, white or green house
  BoolView in_red = newBoolVar(), in_white = newBoolVar(), in_green = newBoolVar();
  int_rel_reif(italy, IRT_EQ, red, in_red);
  int_rel_reif(italy, IRT_EQ, white, in_white);
  int_rel_reif(italy, IRT_EQ, green, in_green);
  vec<BoolView> options;
  options.push(in_red);
  options.push(in_white);
  options.push(in_green);
  bool_clause(options);

  vec<IntVar*> all;
  for (int i = 0; i < 5; ++i) {
    all.push(colors[i]); all.push(nations[i]); all.push(pets[i]); all.push(drinks[i]); all.push(jobs[i]);
  }
  branch(all, VAR_INORDER, VAL_MIN);

  auto to_json = [](vec<IntVar*>& v) {
    json a = json::array();
    for (int i = 0; i < v.size(); ++i) a.push_back(dcp::out(v[i]));
    return a;
  };
  outputs = {{"colors", to_json(colors)}, {"nations", to_json(nations)}, {"jobs", to_json(jobs)},
             {"pets", to_json(pets)}, {"drinks", to_json(drinks)}};
}
