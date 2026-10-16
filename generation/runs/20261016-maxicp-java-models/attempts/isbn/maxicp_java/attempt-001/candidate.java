// ISBN-13 validation and check digit calculation.
// A 13-digit number whose last digit is a check digit; -1 in the input marks an unknown digit.
// The number must start with 978 or 979, and the weighted digit sum (weights 1 and 3 alternating,
// starting with 1) must be a multiple of 10.

import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // the 13 digits of the ISBN, each 0..9
    int[] init = inst.getIntArray("isbn_init");
    CPIntVar[] d = new CPIntVar[13];
    for (int i = 0; i < 13; i++) {
      d[i] = m.intVar(0, 9);
    }

    // a given digit keeps its value
    for (int i = 0; i < 13; i++) {
      if (init[i] >= 0) {
        m.cp().post(eq(d[i], init[i]));
      }
    }

    // the number starts with 978 or 979
    m.cp().post(eq(d[0], 9));
    m.cp().post(eq(d[1], 7));
    // the third digit is 8 or 9
    m.cp().post(ge(d[2], 8));

    // the first 12 digits are multiplied alternately by 1 and 3, starting with 1,
    // and the check digit is (10 - (sum % 10)) % 10, so the weighted sum of all 13
    // digits (the check digit has weight 1) is a multiple of 10
    CPIntVar[] terms = new CPIntVar[13];
    for (int i = 0; i < 13; i++) {
      terms[i] = (i % 2 == 0) ? d[i] : mul(d[i], 3);
    }
    CPIntVar total = sum(terms);
    // the weighted sum is at most 9 * (7 * 1 + 6 * 3) = 225, so the multiple of 10 is at most 22
    CPIntVar tens = m.intVar(0, 25);
    m.cp().post(eq(total, mul(tens, 10)));

    out.put("isbn", d);
  }
}
