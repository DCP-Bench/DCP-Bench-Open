// Dinner problem: choose how many grandparents (1 to 6), parents (1 to 10) and
// children (1 to 40) go to dinner. Grandparents cost $3, parents $2 and children
// $0.50 each. There must be 20 people in total and the dinner must cost $20.
// Output: the number of grandparents, parents and children going to dinner.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  // the problem data is fixed by the statement; the instance carries no fields
  (void)instance;

  // we are going out to dinner taking 1-6 grandparents
  dcp::Lin grandparents = dcp::new_var(h, 1, 6);
  // 1-10 parents
  dcp::Lin parents = dcp::new_var(h, 1, 10);
  // and/or 1-40 children
  dcp::Lin children = dcp::new_var(h, 1, 40);

  // there must be 20 total people at dinner
  dcp::add_row(h, grandparents + parents + children, 20, 20);

  // it must cost $20: grandparents $3, parents $2, children $0.50.
  // Every price is doubled so the coefficients are whole numbers:
  // grandparents $6, parents $4, children $1, total $40
  dcp::add_row(h, 6.0 * grandparents + 4.0 * parents + 1.0 * children, 40, 40);

  out.add("grandparents", grandparents);
  out.add("parents", parents);
  out.add("children", children);
}
