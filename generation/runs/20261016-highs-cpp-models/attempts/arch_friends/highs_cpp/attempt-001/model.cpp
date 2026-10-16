// arch_friends: Harriet bought four pairs of shoes (ecru espadrilles, fuchsia flats,
// purple pumps, suede sandals) at four stores (Foot Farm, Heels in a Handcart, The Shoe
// Palace, Tootsies), one pair per stop. Find the stop number (1 to 4) of each shoe and of each store.
//
// The problem fixes four shoes and four stores, so the sizes are constants of the problem.
// The description has no instance fields, so the instance argument is not read.
#include "dcp.h"

namespace {

const int N = 4;  // four shoes, four stores, four stops

// One shoe or store: one-hot binaries b[k] (1 means it is the stop k + 1).
using Row = std::vector<dcp::Lin>;

Row one_hot_entity(Highs& h) {
  // each shoe and each store is visited at exactly one stop
  Row b;
  dcp::Lin sum;
  for (int k = 0; k < N; ++k) {
    b.push_back(dcp::new_var(h, 0, 1));
    sum = sum + b.back();
  }
  dcp::add_row(h, sum, 1, 1);
  return b;
}

// The stop number of a shoe or store: sum of (k + 1) * b[k].
dcp::Lin stop_of(const Row& b) {
  dcp::Lin s;
  for (int k = 0; k < N; ++k) s = s + double(k + 1) * b[k];
  return s;
}

// the shoes (or the stores) are all different: each stop is used by exactly one of them
void one_per_stop(Highs& h, const std::vector<Row>& group) {
  for (int k = 0; k < N; ++k) {
    dcp::Lin sum;
    for (const Row& r : group) sum = sum + r[k];
    dcp::add_row(h, sum, 1, 1);
  }
}

}  // namespace

void build(const json& /*instance*/, Highs& h, dcp::Outputs& out) {
  Row ecru = one_hot_entity(h);
  Row fuchsia = one_hot_entity(h);
  Row purple = one_hot_entity(h);
  Row suede = one_hot_entity(h);
  Row farm = one_hot_entity(h);
  Row heels = one_hot_entity(h);
  Row palace = one_hot_entity(h);
  Row toots = one_hot_entity(h);
  one_per_stop(h, {ecru, fuchsia, purple, suede});
  one_per_stop(h, {farm, heels, palace, toots});

  // Harriet bought fuchsia flats at Heels in a Handcart.
  dcp::add_row(h, stop_of(fuchsia) - stop_of(heels), 0, 0);

  // The store she visited just after buying her purple pumps was not Tootsies.
  // Let d = Tootsies stop - purple pumps stop, in -3..3. The condition is d != 1.
  // z = 1 gives d >= 2, z = 0 gives d <= 0.
  dcp::Lin z = dcp::new_var(h, 0, 1);
  dcp::Lin d = stop_of(toots) - stop_of(purple);
  dcp::add_row(h, d - double(N + 1) * z, -double(N - 1), kHighsInf);
  dcp::add_row(h, d - double(N - 1) * z, -kHighsInf, 0);

  // The Foot Farm was Harriet's second stop.
  dcp::add_row(h, stop_of(farm), 2, 2);

  // Two stops after The Shoe Palace, Harriet bought her suede sandals.
  dcp::add_row(h, stop_of(suede) - stop_of(palace), 2, 2);

  out.add("ecruespadrilles", stop_of(ecru));
  out.add("fuchsiaflats", stop_of(fuchsia));
  out.add("purplepumps", stop_of(purple));
  out.add("suedesandals", stop_of(suede));
  out.add("footfarm", stop_of(farm));
  out.add("heelsinahandcart", stop_of(heels));
  out.add("theshoepalace", stop_of(palace));
  out.add("tootsies", stop_of(toots));
}
