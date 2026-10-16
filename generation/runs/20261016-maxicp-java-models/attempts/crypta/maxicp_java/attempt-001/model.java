// Cryptarithmetic puzzle: add two 20-letter words and get a third 20-letter word.
// Every letter stands for a different digit 0..9, and the first letter of each
// word is not zero. The output gives the digit of each letter A..J.

import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  // the first summand, the second summand and the sum, most significant letter first
  static final String FIRST = "BAIJJAJIIAHFCFEBBJEA";
  static final String SECOND = "DHFGABCDIDBIFFAGFEJE";
  static final String SUM = "GJEGACDDHFAFJBFIHEEF";

  public static void build(Instance inst, Model m, Outputs out) {
    int width = FIRST.length();

    // each letter A..J is one digit
    CPIntVar[] digit = new CPIntVar[10];
    for (int d = 0; d < 10; d++) {
      digit[d] = m.intVar(0, 9);
    }
    // all letters are distinct digits
    m.cp().post(allDifferent(digit));

    // the first letter of each number cannot be zero
    m.cp().post(ge(digit[FIRST.charAt(0) - 'A'], 1));
    m.cp().post(ge(digit[SECOND.charAt(0) - 'A'], 1));
    m.cp().post(ge(digit[SUM.charAt(0) - 'A'], 1));

    // carry[k] is the carry from column k into the column on its left (column 0 is the
    // leftmost); there is no carry out of the leftmost column and none into the rightmost
    CPIntVar[] carry = new CPIntVar[width];
    for (int k = 1; k < width; k++) {
      carry[k] = m.intVar(0, 1);
    }

    // column by column, the digits of the two summands plus the carry from the right
    // equal the digit of the sum plus ten times the carry to the left
    for (int k = 0; k < width; k++) {
      CPIntVar first = digit[FIRST.charAt(k) - 'A'];
      CPIntVar second = digit[SECOND.charAt(k) - 'A'];
      CPIntVar result = digit[SUM.charAt(k) - 'A'];
      CPIntVar[] addends = (k < width - 1)
          ? new CPIntVar[] {first, second, carry[k + 1]}
          : new CPIntVar[] {first, second};
      CPIntVar[] total = (k > 0)
          ? new CPIntVar[] {result, mul(carry[k], 10)}
          : new CPIntVar[] {result};
      m.cp().post(eq(sum(addends), sum(total)));
    }

    for (int d = 0; d < 10; d++) {
      out.put(String.valueOf((char) ('A' + d)), digit[d]);
    }
  }
}
