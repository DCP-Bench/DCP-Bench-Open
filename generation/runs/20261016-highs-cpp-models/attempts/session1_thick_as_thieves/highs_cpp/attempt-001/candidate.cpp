// Thick as thieves (Sparkles the Jeweller's robbery): six suspects are interviewed.
// Guilty suspects lie, innocent suspects tell the truth. Output: 1 if guilty, 0 if innocent.
// Each suspect's guilt is the negation of the truth of his statement, so for every
// suspect: guilty = 1 - (statement is true).
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  // Guilt of each suspect, 0 or 1.
  dcp::Lin artie = dcp::new_var(h, 0, 1);
  dcp::Lin bill = dcp::new_var(h, 0, 1);
  dcp::Lin crackitt = dcp::new_var(h, 0, 1);
  dcp::Lin dodgy = dcp::new_var(h, 0, 1);
  dcp::Lin edgy = dcp::new_var(h, 0, 1);
  dcp::Lin fingers = dcp::new_var(h, 0, 1);

  // Total number of guilty suspects.
  dcp::Lin guilty_count = artie + bill + crackitt + dodgy + edgy + fingers;

  // the getaway car was barely big enough to hold two, so at least four were innocent:
  // at most two of the six are guilty
  dcp::add_row(h, guilty_count, -kHighsInf, 2);

  // Artie: "It wasn't me." The statement is "not Artie", which is false exactly when Artie
  // is guilty. This holds for either value of artie, so it adds no row.

  // Bill: "Crackitt was in it up to his neck." The statement is true exactly when Crackitt
  // is guilty, so Bill is guilty exactly when Crackitt is innocent.
  dcp::add_row(h, bill + crackitt, 1, 1);

  // Crackitt: "No I wasn't." The statement is "not Crackitt", which is false exactly when
  // Crackitt is guilty. This holds for either value of crackitt, so it adds no row.

  // Dodgy: "If Crackitt did it, Bill did it with him." The statement is true unless Crackitt
  // is guilty and Bill is innocent. Dodgy is guilty exactly when the statement is false.
  // With truth = 1 - dodgy and truth = max(1 - crackitt, bill):
  dcp::add_row(h, crackitt - dodgy, 0, kHighsInf);           // truth >= 1 - crackitt
  dcp::add_row(h, dodgy + bill, -kHighsInf, 1);              // truth >= bill
  dcp::add_row(h, crackitt - dodgy - bill, -kHighsInf, 0);   // truth <= 1 - crackitt + bill

  // Edgy: "Nobody did it alone." The statement is false exactly when exactly one suspect is
  // guilty. Let none = 1 when nobody is guilty, two_or_more = 1 when at least two are guilty.
  // Edgy is guilty exactly when the lone-guilty case holds (edgy = 1 when the count is one).
  dcp::Lin none = dcp::new_var(h, 0, 1);
  dcp::Lin two_or_more = dcp::new_var(h, 0, 1);
  // exactly one of the three cases holds
  dcp::add_row(h, none + two_or_more + edgy, 1, 1);
  // nobody guilty: the count is 0
  dcp::add_row(h, guilty_count + 6 * none, -kHighsInf, 6);
  // at least two guilty: the count is at least 2
  dcp::add_row(h, guilty_count - 2 * two_or_more, 0, kHighsInf);
  // Edgy guilty (exactly one guilty): the count is exactly 1
  dcp::add_row(h, guilty_count + 5 * edgy, -kHighsInf, 6);   // count <= 1 when edgy = 1
  dcp::add_row(h, guilty_count - edgy, 0, kHighsInf);        // count >= 1 when edgy = 1

  // Fingers: "That's right: it was Artie and Dodgy together." The statement is true exactly
  // when Artie and Dodgy are both guilty, so Fingers is guilty exactly when that is not so.
  // fingers = 1 - artie * dodgy:
  dcp::add_row(h, fingers + artie, 1, kHighsInf);            // fingers >= 1 - artie
  dcp::add_row(h, fingers + dodgy, 1, kHighsInf);            // fingers >= 1 - dodgy
  dcp::add_row(h, fingers + artie + dodgy, -kHighsInf, 2);   // fingers <= 2 - artie - dodgy

  out.add("artie", artie);
  out.add("bill", bill);
  out.add("crackitt", crackitt);
  out.add("dodgy", dodgy);
  out.add("edgy", edgy);
  out.add("fingers", fingers);
}
