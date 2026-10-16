// Find a 10 digit number that uses each of the digits 0 to 9 exactly once and
// where the number formed by the first n digits is divisible by n (n = 1 to 10).
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // the digits of the number, read from left to right
    CPIntVar[] d = m.intVarArray(10, 0, 9);
    int[] pow10 = {1, 10, 100, 1000, 10000, 100000, 1000000, 10000000, 100000000, 1000000000};

    // uses each of the digits 0 to 9 exactly once
    m.cp().post(allDifferent(d));

    // a 10 digit number does not start with 0
    m.cp().post(neq(d[0], 0));

    // the number formed by the first n digits is divisible by n, for n = 1 to 7
    // (prefixes of up to 7 digits have small domains; longer prefixes use digit rules below)
    for (int n = 1; n <= 7; n++) {
      CPIntVar[] terms = new CPIntVar[n];
      for (int i = 0; i < n; i++) {
        terms[i] = mul(d[i], pow10[n - 1 - i]);
      }
      CPIntVar prefix = sum(terms);
      // quotient q with prefix == n * q
      CPIntVar q = m.intVar(0, (pow10[n] - 1) / n);
      m.cp().post(eq(prefix, mul(q, n)));
    }

    // the first 8 digits are divisible by 8 when their last three digits are
    // (1000 is a multiple of 8): the value 100*d[5] + 10*d[6] + d[7] is divisible by 8
    CPIntVar last3 = sum(new CPIntVar[] {mul(d[5], 100), mul(d[6], 10), d[7]});
    CPIntVar q8 = m.intVar(0, 999 / 8);
    m.cp().post(eq(last3, mul(q8, 8)));

    // the first 9 digits are divisible by 9 when their digit sum is divisible by 9
    // (a number and its digit sum agree mod 9)
    CPIntVar[] first9 = new CPIntVar[9];
    for (int i = 0; i < 9; i++) {
      first9[i] = d[i];
    }
    CPIntVar digitSum9 = sum(first9);
    CPIntVar q9 = m.intVar(0, 45 / 9);
    m.cp().post(eq(digitSum9, mul(q9, 9)));

    // the whole 10 digit number is divisible by 10, so its last digit is 0
    m.cp().post(eq(d[9], 0));

    out.putDigits("number", d, 10);
  }
}
