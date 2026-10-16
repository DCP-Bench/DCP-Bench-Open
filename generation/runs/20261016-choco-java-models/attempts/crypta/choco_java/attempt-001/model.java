import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Cryptarithm: BAIJJAJIIAHFCFEBBJEA + DHFGABCDIDBIFFAGFEJE = GJEGACDDHFAFJBFIHEEF, where each
// letter stands for a distinct digit 0..9 and the leading letters B, D and G are not zero.
// Solve for the digit of each letter A..J.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // one digit variable per letter, all distinct
    IntVar[] letter = m.intVarArray("letter", 10, 0, 9);
    String names = "ABCDEFGHIJ";
    m.allDifferent(letter, "AC").post();
    IntVar A = letter[0], B = letter[1], C = letter[2], D = letter[3], E = letter[4];
    IntVar F = letter[5], G = letter[6], H = letter[7], I = letter[8], J = letter[9];

    // the first letter of each number is nonzero
    m.arithm(B, "!=", 0).post();
    m.arithm(D, "!=", 0).post();
    m.arithm(G, "!=", 0).post();

    // the three numbers, written from the most significant digit, as letters
    String first = "BAIJJAJIIAHFCFEBBJEA";
    String second = "DHFGABCDIDBIFFAGFEJE";
    String sum = "GJEGACDDHFAFJBFIHEEF";
    int width = first.length();

    // column addition from the least significant digit; carry[p] is the carry into column p
    IntVar[] carry = m.intVarArray("carry", width + 1, 0, 1);
    m.arithm(carry[0], "=", 0).post();      // no carry into the units column
    m.arithm(carry[width], "=", 0).post();  // the sum has the same number of digits, no final carry

    for (int p = 0; p < width; p++) {
      // position counted from the right: column p holds one digit of each number
      int from = width - 1 - p;
      IntVar a = letter[names.indexOf(first.charAt(from))];
      IntVar b = letter[names.indexOf(second.charAt(from))];
      IntVar s = letter[names.indexOf(sum.charAt(from))];
      // digit of the first + digit of the second + carry in = digit of the sum + 10 * carry out
      m.scalar(new IntVar[]{a, b, carry[p], s, carry[p + 1]}, new int[]{1, 1, 1, -1, -10}, "=", 0).post();
    }

    for (int k = 0; k < 10; k++) out.put(names.substring(k, k + 1), letter[k]);
  }
}
