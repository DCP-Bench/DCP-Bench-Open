// Exodus story puzzle: five children (Bernice, Carl, Debby, Sammy, Ted) with ages three, five,
// seven, eight, ten; families from Ethiopia, Kazakhstan, Lithuania, Morocco, Yemen; and stories
// burning bush, captivity, Moses's youth, Passover, Ten Commandments. Find each child's age,
// country and story. Five entities (numbered 1..5) bundle one child, one age, one country and one
// story each. The outputs give, for each slot, the entity number it belongs to.
#include "dcp.h"

namespace {

const int N = 5;                                   // five children, ages, countries, stories
const double AGE_VALUE[N] = {3, 5, 7, 8, 10};      // ages[0] is three, ...

// Adds a binary column.
dcp::Lin bin(Highs& h) { return dcp::new_var(h, 0, 1, true); }

}  // namespace

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  (void)instance;  // the fixed description has no instance data

  // chd[e][c] = 1 when entity e is child c; agc[e][a] = 1 when entity e has age a;
  // cty[e][k] = 1 when entity e has country k; sty[e][s] = 1 when entity e tells story s.
  std::vector<std::vector<dcp::Lin>> chd(N, std::vector<dcp::Lin>(N)), agc = chd, cty = chd, sty = chd;
  for (int e = 0; e < N; ++e)
    for (int k = 0; k < N; ++k) {
      chd[e][k] = bin(h);
      agc[e][k] = bin(h);
      cty[e][k] = bin(h);
      sty[e][k] = bin(h);
    }

  // Each entity has exactly one child, one age, one country and one story.
  for (int e = 0; e < N; ++e) {
    dcp::Lin c1 = 0.0, c2 = 0.0, c3 = 0.0, c4 = 0.0;
    for (int k = 0; k < N; ++k) {
      c1 = c1 + chd[e][k];
      c2 = c2 + agc[e][k];
      c3 = c3 + cty[e][k];
      c4 = c4 + sty[e][k];
    }
    dcp::add_row(h, c1, 1, 1);
    dcp::add_row(h, c2, 1, 1);
    dcp::add_row(h, c3, 1, 1);
    dcp::add_row(h, c4, 1, 1);
  }

  // Each child, age, country and story belongs to exactly one entity.
  for (int k = 0; k < N; ++k) {
    dcp::Lin a1 = 0.0, a2 = 0.0, a3 = 0.0, a4 = 0.0;
    for (int e = 0; e < N; ++e) {
      a1 = a1 + chd[e][k];
      a2 = a2 + agc[e][k];
      a3 = a3 + cty[e][k];
      a4 = a4 + sty[e][k];
    }
    dcp::add_row(h, a1, 1, 1);
    dcp::add_row(h, a2, 1, 1);
    dcp::add_row(h, a3, 1, 1);
    dcp::add_row(h, a4, 1, 1);
  }

  // The age of entity e, as a number of years.
  std::vector<dcp::Lin> age(N);
  for (int e = 0; e < N; ++e) {
    dcp::Lin v = 0.0;
    for (int a = 0; a < N; ++a) v = v + AGE_VALUE[a] * agc[e][a];
    age[e] = v;
  }

  // Ages differ by at most max(AGE_VALUE) - min(AGE_VALUE) = 7, which bounds the big-M constants.
  const double MAX_DIFF = AGE_VALUE[N - 1] - AGE_VALUE[0];

  // If two entities b1 and b2 are both chosen, the age of x minus the age of y lies in [lo, hi].
  auto when_both = [&](const dcp::Lin& b1, const dcp::Lin& b2, const dcp::Lin& x, const dcp::Lin& y,
                       double lo, double hi) {
    dcp::Lin diff = x - y;
    dcp::Lin both = b1 + b2;
    double mu = MAX_DIFF - hi;   // upper row: diff <= hi + mu (2 - both)
    double ml = lo + MAX_DIFF;   // lower row: diff >= lo - ml (2 - both)
    if (hi < kHighsInf) dcp::add_row(h, diff + mu * both, -kHighsInf, hi + 2 * mu);
    if (lo > -kHighsInf) dcp::add_row(h, diff - ml * both, lo - 2 * ml, kHighsInf);
  };

  // Debby (child 2) is from Lithuania (country 2): the same entity has both.
  // Debby's family is from Lithuania.
  for (int e = 0; e < N; ++e) dcp::add_row(h, chd[e][2] - cty[e][2], 0, 0);

  // The child who told the Passover story (story 3) is two years older than Bernice (child 0).
  // The Passover child is two years older than Bernice.
  for (int e = 0; e < N; ++e)
    for (int f = 0; f < N; ++f)
      when_both(sty[e][3], chd[f][0], age[e], age[f], 2, 2);

  // The child whose family is from Yemen (country 4) is younger than the child from the Ethiopian
  // family (country 0). The Yemen child is younger than the Ethiopian child.
  for (int e = 0; e < N; ++e)
    for (int f = 0; f < N; ++f)
      when_both(cty[e][4], cty[f][0], age[e], age[f], -kHighsInf, -1);

  // The child from the Moroccan family (country 3) is three years older than Ted (child 4).
  // The Moroccan child is three years older than Ted.
  for (int e = 0; e < N; ++e)
    for (int f = 0; f < N; ++f)
      when_both(cty[e][3], chd[f][4], age[e], age[f], 3, 3);

  // Sammy (child 3) is three years older than the child who told the story of Moses's youth
  // (story 2). Sammy is three years older than the Moses's youth child.
  for (int e = 0; e < N; ++e)
    for (int f = 0; f < N; ++f)
      when_both(chd[e][3], sty[f][2], age[e], age[f], 3, 3);

  // Outputs: for each slot, the number (1..5) of the entity that fills it.
  std::vector<dcp::Lin> ages(N), children(N), countries(N), stories(N);
  for (int k = 0; k < N; ++k) {
    dcp::Lin ea = 0.0, ec = 0.0, ek = 0.0, es = 0.0;
    for (int e = 0; e < N; ++e) {
      ea = ea + (e + 1) * agc[e][k];
      ec = ec + (e + 1) * chd[e][k];
      ek = ek + (e + 1) * cty[e][k];
      es = es + (e + 1) * sty[e][k];
    }
    ages[k] = ea;
    children[k] = ec;
    countries[k] = ek;
    stories[k] = es;
  }
  out.add("ages", ages);
  out.add("children", children);
  out.add("countries", countries);
  out.add("stories", stories);
}
