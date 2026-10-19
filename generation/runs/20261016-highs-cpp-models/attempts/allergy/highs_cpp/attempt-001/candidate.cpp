// Allergy puzzle: four friends, Debra (0), Janet (1), Hugh (2) and Rick (3), are
// each allergic to something different (eggs, mold, nuts, ragweed) and each has a
// different surname (Baxter, Lemon, Malone, Fleet). Each food and each surname is
// reported as the index of the friend it belongs to.
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  (void)instance;  // the problem has no instance fields; the data is fixed by the statement
  const int friends = 4;
  // Food order: 0 eggs, 1 mold, 2 nuts, 3 ragweed.
  // Surname order: 0 Baxter, 1 Lemon, 2 Malone, 3 Fleet.
  // allergy[f][c] = 1 if friend f is allergic to food c.
  // surname[f][k] = 1 if friend f has surname k.
  std::vector<std::vector<dcp::Lin>> allergy(friends, std::vector<dcp::Lin>(friends));
  std::vector<std::vector<dcp::Lin>> surname(friends, std::vector<dcp::Lin>(friends));
  for (int f = 0; f < friends; ++f) {
    for (int c = 0; c < friends; ++c) {
      allergy[f][c] = dcp::new_var(h, 0, 1);
      surname[f][c] = dcp::new_var(h, 0, 1);
    }
  }

  // each friend is allergic to exactly one food
  for (int f = 0; f < friends; ++f) {
    dcp::Lin row;
    for (int c = 0; c < friends; ++c) row = row + allergy[f][c];
    dcp::add_row(h, row, 1, 1);
  }
  // each food is the allergy of exactly one friend
  for (int c = 0; c < friends; ++c) {
    dcp::Lin row;
    for (int f = 0; f < friends; ++f) row = row + allergy[f][c];
    dcp::add_row(h, row, 1, 1);
  }
  // each friend has exactly one surname
  for (int f = 0; f < friends; ++f) {
    dcp::Lin row;
    for (int k = 0; k < friends; ++k) row = row + surname[f][k];
    dcp::add_row(h, row, 1, 1);
  }
  // each surname belongs to exactly one friend
  for (int k = 0; k < friends; ++k) {
    dcp::Lin row;
    for (int f = 0; f < friends; ++f) row = row + surname[f][k];
    dcp::add_row(h, row, 1, 1);
  }

  // Rick is not allergic to mold
  dcp::add_row(h, allergy[3][1], 0, 0);
  // Baxter is allergic to eggs: whoever is surnamed Baxter is allergic to eggs
  for (int f = 0; f < friends; ++f) {
    dcp::add_row(h, surname[f][0] - allergy[f][0], -kHighsInf, 0);
  }
  // Hugh is neither surnamed Lemon nor Fleet
  dcp::add_row(h, surname[2][1], 0, 0);
  dcp::add_row(h, surname[2][3], 0, 0);
  // Debra is allergic to ragweed
  dcp::add_row(h, allergy[0][3], 1, 1);
  // Janet (who isn't Lemon) is neither allergic to eggs nor to mold
  dcp::add_row(h, surname[1][1], 0, 0);
  dcp::add_row(h, allergy[1][0], 0, 0);
  dcp::add_row(h, allergy[1][1], 0, 0);

  // Outputs: for each food and surname, the index of the friend who has it.
  const char* foods[friends] = {"eggs", "mold", "nuts", "ragweed"};
  const char* surnames[friends] = {"baxter", "lemon", "malone", "fleet"};
  for (int c = 0; c < friends; ++c) {
    dcp::Lin who;
    for (int f = 0; f < friends; ++f) {
      who = who + static_cast<double>(f) * allergy[f][c];
    }
    out.add(foods[c], who);
  }
  for (int k = 0; k < friends; ++k) {
    dcp::Lin who;
    for (int f = 0; f < friends; ++f) {
      who = who + static_cast<double>(f) * surname[f][k];
    }
    out.add(surnames[k], who);
  }
}
