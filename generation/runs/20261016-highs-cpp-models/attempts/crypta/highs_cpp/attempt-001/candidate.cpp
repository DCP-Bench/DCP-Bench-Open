// Cryptarithmetic puzzle: a 20-letter sum of two numbers equals a 20-letter number.
// All letters A..J are distinct digits 0..9, and the first letter of each number is not zero.
// Output: the digit of each letter A..J.
#include <string>
#include <vector>

#include "dcp.h"

namespace {
const char* kFirst = "BAIJJAJIIAHFCFEBBJEA";
const char* kSecond = "DHFGABCDIDBIFFAGFEJE";
const char* kSum = "GJEGACDDHFAFJBFIHEEF";
const int kLen = 20;
const int kLetters = 10;
}  // namespace

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  (void)instance;  // the puzzle has no instance data

  // y[L][v] = 1 when letter L (0 = A) takes digit v.
  std::vector<std::vector<dcp::Lin>> y(kLetters, std::vector<dcp::Lin>(10));
  for (int L = 0; L < kLetters; ++L)
    for (int v = 0; v < 10; ++v) y[L][v] = dcp::new_var(h, 0, 1);

  // digit[L] = sum_v v y[L][v], the digit of letter L.
  std::vector<dcp::Lin> digit(kLetters);
  for (int L = 0; L < kLetters; ++L) {
    dcp::Lin e;
    for (int v = 0; v < 10; ++v) e = e + static_cast<double>(v) * y[L][v];
    digit[L] = e;
  }

  // each letter takes exactly one digit
  for (int L = 0; L < kLetters; ++L) {
    dcp::Lin one;
    for (int v = 0; v < 10; ++v) one = one + y[L][v];
    dcp::add_row(h, one, 1, 1);
  }

  // all letters are different: each digit is used by exactly one letter
  for (int v = 0; v < 10; ++v) {
    dcp::Lin one;
    for (int L = 0; L < kLetters; ++L) one = one + y[L][v];
    dcp::add_row(h, one, 1, 1);
  }

  // the first letter of each number is not zero: B, D and G are not 0
  const char leading[] = {'B', 'D', 'G'};
  for (char c : leading) dcp::add_row(h, y[c - 'A'][0], 0, 0);

  // carry[i] is the carry out of column i (counted from the left), carry[i+1] is the carry into it
  // from the right. The leftmost carry out and the rightmost carry in are zero.
  std::vector<dcp::Lin> carry(kLen + 1);
  carry[0] = 0;
  carry[kLen] = 0;
  for (int i = 1; i < kLen; ++i) carry[i] = dcp::new_var(h, 0, 1);

  // column sums: first digit + second digit + carry in = sum digit + 10 carry out
  for (int i = 0; i < kLen; ++i) {
    int a = kFirst[i] - 'A';
    int b = kSecond[i] - 'A';
    int c = kSum[i] - 'A';
    dcp::add_row(h, digit[a] + digit[b] + carry[i + 1] - digit[c] - 10.0 * carry[i], 0, 0);
  }

  for (int L = 0; L < kLetters; ++L) out.add(std::string(1, static_cast<char>('A' + L)), digit[L]);
}
