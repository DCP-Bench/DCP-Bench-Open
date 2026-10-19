// Abbot's puzzle: 100 bushels of corn are distributed among 100 people. Each man
// receives three bushels, each woman two, and each child half a bushel. There are
// five times as many women as men. Find the number of men, women and children.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  (void)instance;
  const double people = 100;
  const double bushels = 100;

  // the number of men, women and children are whole numbers from 0 to the number of people
  dcp::Lin men = dcp::new_var(h, 0, people);
  dcp::Lin women = dcp::new_var(h, 0, people);
  dcp::Lin children = dcp::new_var(h, 0, people);

  // the 100 people are men, women and children
  dcp::add_row(h, men + women + children, people, people);

  // each man receives three bushels, each woman two, and each child half a bushel;
  // together they receive 100 bushels (every amount is doubled so that all coefficients are whole)
  dcp::add_row(h, 6.0 * men + 4.0 * women + 1.0 * children, 2 * bushels, 2 * bushels);

  // there are five times as many women as men
  dcp::add_row(h, women - 5.0 * men, 0, 0);

  out.add("men", men);
  out.add("women", women);
  out.add("children", children);
}
