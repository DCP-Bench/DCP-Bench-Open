// Contracting costs: a contractor planning a house pays six men (paper hanger, painter,
// plumber, electrician, carpenter, mason) for pairs of services. Each pair has a total:
// the paper hanger and the painter $1,100; the painter and the plumber $1,700; the plumber
// and the electrician $1,100; the electrician and the carpenter $3,300; the carpenter and
// the mason $5,300; the mason and the painter $3,200. Find what each man charges.
#include "dcp.h"

void build(const json& /*instance*/, Highs& h, dcp::Outputs& out) {
  // each charge is a whole number of dollars, no more than the largest pair total of $5,300
  dcp::Lin paper_hanger = dcp::new_var(h, 0, 5300);
  dcp::Lin painter = dcp::new_var(h, 0, 5300);
  dcp::Lin plumber = dcp::new_var(h, 0, 5300);
  dcp::Lin electrician = dcp::new_var(h, 0, 5300);
  dcp::Lin carpenter = dcp::new_var(h, 0, 5300);
  dcp::Lin mason = dcp::new_var(h, 0, 5300);

  // the paper hanger and the painter together charge $1,100
  dcp::add_row(h, paper_hanger + painter, 1100, 1100);
  // the painter and the plumber together charge $1,700
  dcp::add_row(h, painter + plumber, 1700, 1700);
  // the plumber and the electrician together charge $1,100
  dcp::add_row(h, plumber + electrician, 1100, 1100);
  // the electrician and the carpenter together charge $3,300
  dcp::add_row(h, electrician + carpenter, 3300, 3300);
  // the carpenter and the mason together charge $5,300
  dcp::add_row(h, carpenter + mason, 5300, 5300);
  // the mason and the painter together charge $3,200
  dcp::add_row(h, mason + painter, 3200, 3200);

  out.add("paper_hanger", paper_hanger);
  out.add("painter", painter);
  out.add("plumber", plumber);
  out.add("electrician", electrician);
  out.add("carpenter", carpenter);
  out.add("mason", mason);
}
