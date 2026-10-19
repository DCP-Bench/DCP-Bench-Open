#include "dcp.h"

// Alice gives Bob change of a given amount, using coins from a set of coin types.
// Each coin type has a value and a number of coins available. Choose how many
// coins of each type to give so that the change adds up to the amount, and the
// total number of coins used is as small as possible.
// Output coin_counts: the number of coins of each type given to Bob.

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  // The amount of change to give (in the same unit as the coin values).
  int amount = instance.at("amount").get<int>();
  // The value of each coin type, and how many coins of that type are available.
  std::vector<int> values = instance.at("types_of_coins").get<std::vector<int>>();
  std::vector<int> available = instance.at("available_coins").get<std::vector<int>>();

  // coin_counts[i] = number of coins of type i given to Bob.
  // It cannot be negative and cannot exceed the number of coins available.
  std::vector<dcp::Lin> coin_counts;
  for (std::size_t i = 0; i < values.size(); i++) {
    coin_counts.push_back(dcp::new_var(h, 0, available[i]));
  }

  // the coins given add up to the amount of change
  dcp::Lin change_value = 0;
  for (std::size_t i = 0; i < values.size(); i++) {
    change_value = change_value + values[i] * coin_counts[i];
  }
  dcp::add_row(h, change_value, amount, amount);

  // minimise the total number of coins used
  dcp::Lin total_coins = 0;
  for (std::size_t i = 0; i < values.size(); i++) {
    total_coins = total_coins + coin_counts[i];
  }
  out.minimize(total_coins);

  out.add("coin_counts", coin_counts);
}
