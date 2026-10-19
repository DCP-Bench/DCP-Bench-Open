// Dudeney numbers: find a positive integer that is a perfect cube such that the sum
// of its digits equals the cube root of the number. Print such a number that is
// larger than 1. The number has at most n digits (n is read from the instance).
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int n = instance.at("n").get<int>();

  // the digits of the number, least significant first, each from 0 to 9
  std::vector<dcp::Lin> digit;
  for (int i = 0; i < n; i++) digit.push_back(dcp::new_var(h, 0, 9));

  // the number is the sum of each digit times its place value
  dcp::Lin number;
  double place = 1;
  for (int i = 0; i < n; i++) {
    number = number + place * digit[i];
    place *= 10;
  }

  // the cube root is at least 2 (the number is larger than 1) and at most
  // the largest possible digit sum, 9 per digit; root k is picked by pick[k - 2]
  int root_max = 9 * n;
  std::vector<dcp::Lin> pick;
  for (int k = 2; k <= root_max; k++) pick.push_back(dcp::new_var(h, 0, 1));

  // exactly one cube root is picked
  dcp::Lin picked;
  for (const auto& p : pick) picked = picked + p;
  dcp::add_row(h, picked, 1, 1);

  // the number is the cube of the picked root
  dcp::Lin cube_of_root = number;
  for (int k = 2; k <= root_max; k++) cube_of_root = cube_of_root - (double)k * k * k * pick[k - 2];
  dcp::add_row(h, cube_of_root, 0, 0);

  // the sum of the digits equals the picked cube root
  dcp::Lin digit_sum;
  for (const auto& d : digit) digit_sum = digit_sum + d;
  for (int k = 2; k <= root_max; k++) digit_sum = digit_sum - (double)k * pick[k - 2];
  dcp::add_row(h, digit_sum, 0, 0);

  out.add("number", number);
}
