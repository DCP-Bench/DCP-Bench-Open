// Birthday coins: Tommy got 15 coins (half-crowns, shillings and sixpence) that add up
// to one pound, 5 shillings and 6 pence. Output the number of half-crowns (half_crowns).
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  (void)instance;
  // half-crowns, shillings and sixpence are whole numbers of coins
  dcp::Lin half_crowns = dcp::new_var(h, 0, 15);
  dcp::Lin shillings = dcp::new_var(h, 0, 15);
  dcp::Lin sixpence = dcp::new_var(h, 0, 15);

  // he was given 15 coins in all
  dcp::add_row(h, half_crowns + shillings + sixpence, 15, 15);

  // the coins add up to one pound 5 shillings 6 pence, which is 306 pence:
  // a half-crown is 30 pence, a shilling 12 pence, a sixpence 6 pence
  dcp::add_row(h, 30.0 * half_crowns + 12.0 * shillings + 6.0 * sixpence, 306, 306);

  out.add("half_crowns", half_crowns);
}
