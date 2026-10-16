// Exodus stories: five children (Bernice, Carl, Debby, Sammy, Ted) have ages, families' countries and Exodus stories; find the association from the clues.
// Entities are the children, numbered 0..4 in the order given (Bernice, Carl, Debby, Sammy, Ted); output numbers are 1-based child numbers.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  // the five ages in increasing order, the five countries and the five stories are listed in the statement's order
  vec<int> age_values;
  age_values.push(3); age_values.push(5); age_values.push(7); age_values.push(8); age_values.push(10);

  // age_slot[e] is the index in age_values of child e's age; age_of[s] is the child whose age is age_values[s]
  vec<IntVar*> age_slot, age_of;
  createVars(age_slot, 5, 0, 4);
  createVars(age_of, 5, 0, 4);
  inverse(age_slot, age_of);

  // country_slot[e] is the country index of child e (0 Ethiopia, 1 Kazakhstan, 2 Lithuania, 3 Morocco, 4 Yemen); country_of[c] is the child from country c
  vec<IntVar*> country_slot, country_of;
  createVars(country_slot, 5, 0, 4);
  createVars(country_of, 5, 0, 4);
  inverse(country_slot, country_of);

  // story_slot[e] is the story index of child e (0 burning bush, 1 captivity, 2 Moses's youth, 3 Passover, 4 Ten Commandments); story_of[s] is the child telling story s
  vec<IntVar*> story_slot, story_of;
  createVars(story_slot, 5, 0, 4);
  createVars(story_of, 5, 0, 4);
  inverse(story_slot, story_of);

  // the age of each child, read from the age slot
  vec<IntVar*> age;
  for (int e = 0; e < 5; ++e) {
    IntVar* a = newIntVar(3, 10);
    array_int_element(age_slot[e], age_values, a);
    age.push(a);
  }

  // Debby's family is from Lithuania
  int_rel(country_slot[2], IRT_EQ, 2);

  // the child who told the Passover story is two years older than Bernice
  IntVar* passover_age = newIntVar(3, 10);
  array_var_int_element_bound(story_of[3], age, passover_age);
  vec<IntVar*> older_pair;
  older_pair.push(passover_age); older_pair.push(age[0]);
  vec<int> minus_plus;
  minus_plus.push(1); minus_plus.push(-1);
  int_linear(minus_plus, older_pair, IRT_EQ, 2);

  // the child whose family is from Yemen is younger than the child from the Ethiopian family
  IntVar* yemen_age = newIntVar(3, 10);
  array_var_int_element_bound(country_of[4], age, yemen_age);
  IntVar* ethiopia_age = newIntVar(3, 10);
  array_var_int_element_bound(country_of[0], age, ethiopia_age);
  int_rel(yemen_age, IRT_LT, ethiopia_age);

  // the child from the Moroccan family is three years older than Ted
  IntVar* morocco_age = newIntVar(3, 10);
  array_var_int_element_bound(country_of[3], age, morocco_age);
  vec<IntVar*> morocco_pair;
  morocco_pair.push(morocco_age); morocco_pair.push(age[4]);
  int_linear(minus_plus, morocco_pair, IRT_EQ, 3);

  // Sammy is three years older than the child who told the story of Moses's youth
  IntVar* moses_age = newIntVar(3, 10);
  array_var_int_element_bound(story_of[2], age, moses_age);
  vec<IntVar*> sammy_pair;
  sammy_pair.push(age[3]); sammy_pair.push(moses_age);
  int_linear(minus_plus, sammy_pair, IRT_EQ, 3);

  // branch on the slots of each child
  vec<IntVar*> decisions;
  for (int e = 0; e < 5; ++e) { decisions.push(age_slot[e]); }
  for (int e = 0; e < 5; ++e) { decisions.push(country_slot[e]); }
  for (int e = 0; e < 5; ++e) { decisions.push(story_slot[e]); }
  branch(decisions, VAR_INORDER, VAL_MIN);

  // ages[s] is the child (1 to 5) whose age is age_values[s]; children[j] is child j+1; countries and stories are read the same way
  json ages_out = json::array(), children_out = json::array(), countries_out = json::array(), stories_out = json::array();
  for (int s = 0; s < 5; ++s) {
    IntVar* a = newIntVar(1, 5);
    vec<IntVar*> pair; pair.push(a); pair.push(age_of[s]);
    int_linear(minus_plus, pair, IRT_EQ, 1);
    ages_out.push_back(dcp::out(a));
  }
  for (int j = 0; j < 5; ++j) children_out.push_back(dcp::out(getConstant(j + 1)));
  for (int c = 0; c < 5; ++c) {
    IntVar* k = newIntVar(1, 5);
    vec<IntVar*> pair; pair.push(k); pair.push(country_of[c]);
    int_linear(minus_plus, pair, IRT_EQ, 1);
    countries_out.push_back(dcp::out(k));
  }
  for (int s = 0; s < 5; ++s) {
    IntVar* k = newIntVar(1, 5);
    vec<IntVar*> pair; pair.push(k); pair.push(story_of[s]);
    int_linear(minus_plus, pair, IRT_EQ, 1);
    stories_out.push_back(dcp::out(k));
  }
  outputs = {{"ages", ages_out}, {"children", children_out}, {"countries", countries_out}, {"stories", stories_out}};
}
