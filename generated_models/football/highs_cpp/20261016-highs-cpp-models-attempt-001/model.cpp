// Football: a Premiership squad is bought from priced groups of players. Prices are in
// GBP thousands (the statement's GBP millions times 1000), so the total is an integer.
// Spend at most GBP 30 million (30000 thousands), maximise the total spent, and output it (z).
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  // Each player is bought at most once: one binary column per player.
  // Goalkeepers (must buy exactly 1): g1 0.73, g2 1.28, g3 3.88
  std::vector<int> gk_price = {730, 1280, 3880};
  // Defenders (must buy 2 or more): d1 0.92, d2 1.31, d3 1.62, d4 2.41, d5 2.79, d6 3.28, d7 3.91, d8 4.57
  std::vector<int> df_price = {920, 1310, 1620, 2410, 2790, 3280, 3910, 4570};
  // Midfielders (must buy 3 or more): m1 1.8, m2 2.63, m3 3.17, m4 3.769, m5 4.14, m6 4.75, m7 5.38,
  // m8 5.93, m9 6.78, m10 7.13
  std::vector<int> mf_price = {1800, 2630, 3170, 3769, 4140, 4750, 5380, 5930, 6780, 7130};
  // Strikers (must buy 2 or more): s1 4.46, s2 6.47, s3 7.78, s4 8.39, s5 9.5
  std::vector<int> st_price = {4460, 6470, 7780, 8390, 9500};

  auto make_group = [&h](const std::vector<int>& prices) {
    std::vector<dcp::Lin> cols;
    for (size_t i = 0; i < prices.size(); ++i) cols.push_back(dcp::new_var(h, 0, 1));
    return cols;
  };
  auto sum_of = [](const std::vector<dcp::Lin>& cols) {
    dcp::Lin s = 0.0;
    for (const auto& c : cols) s = s + c;
    return s;
  };
  auto spend_of = [](const std::vector<int>& prices, const std::vector<dcp::Lin>& cols) {
    dcp::Lin s = 0.0;
    for (size_t i = 0; i < prices.size(); ++i) s = s + static_cast<double>(prices[i]) * cols[i];
    return s;
  };

  std::vector<dcp::Lin> gk = make_group(gk_price);
  std::vector<dcp::Lin> df = make_group(df_price);
  std::vector<dcp::Lin> mf = make_group(mf_price);
  std::vector<dcp::Lin> st = make_group(st_price);

  // must buy exactly one goalkeeper
  dcp::add_row(h, sum_of(gk), 1, 1);
  // must buy two or more defenders
  dcp::add_row(h, sum_of(df), 2, kHighsInf);
  // must buy three or more midfielders
  dcp::add_row(h, sum_of(mf), 3, kHighsInf);
  // must buy two or more strikers
  dcp::add_row(h, sum_of(st), 2, kHighsInf);

  // at least eleven players in total
  dcp::Lin total_players = sum_of(gk) + sum_of(df) + sum_of(mf) + sum_of(st);
  dcp::add_row(h, total_players, 11, kHighsInf);

  // the total price does not go over GBP 30 million (30000 thousands)
  dcp::Lin total_price = spend_of(gk_price, gk) + spend_of(df_price, df) +
                         spend_of(mf_price, mf) + spend_of(st_price, st);
  dcp::add_row(h, total_price, -kHighsInf, 30000);

  out.add("z", total_price);
  out.maximize(total_price);
}
