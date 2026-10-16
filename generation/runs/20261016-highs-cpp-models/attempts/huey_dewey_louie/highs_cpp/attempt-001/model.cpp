// Huey, Dewey and Louie: the uncle asks whether their statements decide who (if any) is guilty.
// Since they cannot tell a lie, each of the three statements is true.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  // huey, dewey, louie: 1 if the boy is guilty, 0 otherwise
  dcp::Lin huey = dcp::new_var(h, 0, 1);
  dcp::Lin dewey = dcp::new_var(h, 0, 1);
  dcp::Lin louie = dcp::new_var(h, 0, 1);

  // Huey: "Dewey and Louie have equal share in it; if one is guilty, so is the other"
  // so Dewey and Louie are both guilty or both innocent
  dcp::add_row(h, dewey - louie, 0, 0);

  // Dewey: "If Huey is guilty, then so am I"
  // so Huey guilty implies Dewey guilty
  dcp::add_row(h, dewey - huey, 0, kHighsInf);

  // Louie: "Dewey and I are not both guilty"
  // so Dewey and Louie are not both guilty
  dcp::add_row(h, dewey + louie, -kHighsInf, 1);

  out.add("huey", huey);
  out.add("dewey", dewey);
  out.add("louie", louie);
}
