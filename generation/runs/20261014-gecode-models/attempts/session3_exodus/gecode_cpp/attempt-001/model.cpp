// Session 3 Exodus: match five children to an age, a family's country of origin and
// a part of the Exodus story. Each association is a row 0..4; every category is a
// permutation of the rows, so the same row number links the four categories.
#include "dcp.h"

class Exodus : public dcp::Space {
 protected:
  IntVarArray child;    // child[c]: row of child c (0 Bernice, 1 Carl, 2 Debby, 3 Sammy, 4 Ted)
  IntVarArray country;  // country[k]: row of country k (0 Ethiopia, 1 Kazakhstan, 2 Lithuania, 3 Morocco, 4 Yemen)
  IntVarArray story;    // story[s]: row of story s (0 burning bush, 1 captivity, 2 Moses's youth, 3 Passover, 4 Ten Commandments)
  IntVarArray age;      // age[a]: row of the child of age a (0 three, 1 five, 2 seven, 3 eight, 4 ten)
  IntVarArray age_at;   // age_at[r]: age index of row r (inverse of age)
  IntVarArray years;    // years[r]: age in years of row r
  IntVarArray ages_out;      // output: age[a] + 1
  IntVarArray children_out;  // output: child[c] + 1
  IntVarArray countries_out; // output: country[k] + 1
  IntVarArray stories_out;   // output: story[s] + 1

  // age in years of the association in row `row`
  IntVar years_of(const IntVar& row) {
    IntVar y(*this, 3, 10);
    element(*this, years, row, y);
    return y;
  }

 public:
  explicit Exodus(const json& instance) {
    (void)instance;  // the problem has no instance fields; the data is in the statement
    const int n = 5;
    const std::vector<int> age_years = {3, 5, 7, 8, 10};

    child = IntVarArray(*this, n, 0, n - 1);
    country = IntVarArray(*this, n, 0, n - 1);
    story = IntVarArray(*this, n, 0, n - 1);
    age = IntVarArray(*this, n, 0, n - 1);
    age_at = IntVarArray(*this, n, 0, n - 1);
    years = IntVarArray(*this, n, 3, 10);

    // every child, country, story and age belongs to exactly one association
    distinct(*this, child, IPL_DOM);
    distinct(*this, country, IPL_DOM);
    distinct(*this, story, IPL_DOM);
    distinct(*this, age, IPL_DOM);

    // the age slot of each association, and its age in years
    channel(*this, age, age_at);
    for (int r = 0; r < n; ++r) element(*this, IntArgs(age_years), age_at[r], years[r]);

    // Debby's family is from Lithuania
    rel(*this, child[2] == country[2]);

    // the child who told the story of the Passover is two years older than Bernice
    rel(*this, years_of(story[3]) == years_of(child[0]) + 2);

    // the child whose family is from Yemen is younger than the child from the Ethiopian family
    rel(*this, years_of(country[4]) < years_of(country[0]));

    // the child from the Moroccan family is three years older than Ted
    rel(*this, years_of(country[3]) == years_of(child[4]) + 3);

    // Sammy is three years older than the child who told the story of Moses's youth
    rel(*this, years_of(child[3]) == years_of(story[2]) + 3);

    branch(*this, child, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    branch(*this, country, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    branch(*this, story, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    branch(*this, age, INT_VAR_SIZE_MIN(), INT_VAL_MIN());

    // outputs number the associations 1..5
    ages_out = IntVarArray(*this, n, 1, n);
    children_out = IntVarArray(*this, n, 1, n);
    countries_out = IntVarArray(*this, n, 1, n);
    stories_out = IntVarArray(*this, n, 1, n);
    for (int i = 0; i < n; ++i) {
      rel(*this, ages_out[i] == age[i] + 1);
      rel(*this, children_out[i] == child[i] + 1);
      rel(*this, countries_out[i] == country[i] + 1);
      rel(*this, stories_out[i] == story[i] + 1);
    }
    output("ages", ages_out);
    output("children", children_out);
    output("countries", countries_out);
    output("stories", stories_out);
  }

  Exodus(Exodus& s) : dcp::Space(s) {
    child.update(*this, s.child);
    country.update(*this, s.country);
    story.update(*this, s.story);
    age.update(*this, s.age);
    age_at.update(*this, s.age_at);
    years.update(*this, s.years);
    ages_out.update(*this, s.ages_out);
    children_out.update(*this, s.children_out);
    countries_out.update(*this, s.countries_out);
    stories_out.update(*this, s.stories_out);
  }
  Gecode::Space* copy() override { return new Exodus(*this); }
};

DCP_MODEL(Exodus)
