// N fractions: find distinct non-zero digits A..I with A/BC + D/EF + G/HI = 1, where BC, EF and HI
// are the two-digit numbers 10*B + C, 10*E + F and 10*H + I.
// The fractions are cleared of denominators: A*EF*HI + D*BC*HI + G*BC*EF = BC*EF*HI.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  // the nine digits are distinct and non-zero (the problem's own bound, not the instance)
  vec<IntVar*> digits;
  createVars(digits, 9, 1, 9);
  IntVar* A = digits[0];
  IntVar* B = digits[1];
  IntVar* C = digits[2];
  IntVar* D = digits[3];
  IntVar* E = digits[4];
  IntVar* F = digits[5];
  IntVar* G = digits[6];
  IntVar* H = digits[7];
  IntVar* I = digits[8];
  // all nine digits are different
  all_different(digits);

  // the two-digit numbers BC, EF and HI
  IntVar* bc = newIntVar(10, 99);
  IntVar* ef = newIntVar(10, 99);
  IntVar* hi = newIntVar(10, 99);
  vec<int> tens;
  tens.push(10);
  tens.push(1);
  vec<IntVar*> bcd;
  bcd.push(B);
  bcd.push(C);
  int_linear(tens, bcd, IRT_EQ, bc);
  vec<IntVar*> efd;
  efd.push(E);
  efd.push(F);
  int_linear(tens, efd, IRT_EQ, ef);
  vec<IntVar*> hid;
  hid.push(H);
  hid.push(I);
  int_linear(tens, hid, IRT_EQ, hi);

  // products of pairs of two-digit numbers, used to clear the denominators
  IntVar* ef_hi = newIntVar(100, 99 * 99);
  int_times(ef, hi, ef_hi);
  IntVar* bc_hi = newIntVar(100, 99 * 99);
  int_times(bc, hi, bc_hi);
  IntVar* bc_ef = newIntVar(100, 99 * 99);
  int_times(bc, ef, bc_ef);

  // A * EF * HI, D * BC * HI and G * BC * EF are the three numerators after clearing denominators
  IntVar* num_a = newIntVar(100, 9 * 99 * 99);
  int_times(A, ef_hi, num_a);
  IntVar* num_d = newIntVar(100, 9 * 99 * 99);
  int_times(D, bc_hi, num_d);
  IntVar* num_g = newIntVar(100, 9 * 99 * 99);
  int_times(G, bc_ef, num_g);

  // the product BC * EF * HI is the common denominator
  IntVar* common = newIntVar(1000, 99 * 99 * 99);
  int_times(bc_ef, hi, common);

  // the three numerators add up to the common denominator, which makes the fractions sum to 1
  vec<IntVar*> numerators;
  numerators.push(num_a);
  numerators.push(num_d);
  numerators.push(num_g);
  int_linear(numerators, IRT_EQ, common);

  // the digits are the decision variables
  branch(digits, VAR_INORDER, VAL_MIN);

  outputs = {{"A", dcp::out(A)}, {"B", dcp::out(B)}, {"C", dcp::out(C)},
             {"D", dcp::out(D)}, {"E", dcp::out(E)}, {"F", dcp::out(F)},
             {"G", dcp::out(G)}, {"H", dcp::out(H)}, {"I", dcp::out(I)}};
}
