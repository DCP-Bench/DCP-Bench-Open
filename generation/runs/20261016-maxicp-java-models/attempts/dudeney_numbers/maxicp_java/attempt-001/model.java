// Dudeney numbers: a positive integer that is a perfect cube, such that the sum of its
// digits equals the cube root of the number. Print such a number that is larger than 1.
// The instance field n is the number of digits the printed number may have.
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");

    // the number has at most n digits, so it is below 10^n
    long limit = 1;
    for (int i = 0; i < n; i++) limit *= 10;

    // the largest cube root k with k^3 below that limit
    int root = 0;
    while ((long) (root + 1) * (root + 1) * (root + 1) < limit) root++;

    // the cubes of 0..root
    int[] cubes = new int[root + 1];
    for (int k = 0; k <= root; k++) cubes[k] = k * k * k;

    // the cube root of the number
    CPIntVar k = m.intVar(0, root);

    // the number is a perfect cube: the number equals the cube of k
    CPIntVar number = m.intVar(0, cubes[root]);
    m.cp().post(eq(number, element(cubes, k)));

    // the number is larger than 1
    m.cp().post(ge(number, 2));

    // the number is written with n digits, each from 0 to 9
    CPIntVar[] digits = m.intVarArray(n, 0, 9);

    // the number is the value of its digits
    CPIntVar[] terms = new CPIntVar[n];
    long place = 1;
    for (int i = 0; i < n; i++) {
      terms[i] = mul(digits[i], (int) place);
      place *= 10;
    }
    m.cp().post(sum(terms, number));

    // the sum of its digits equals the cube root of the number
    m.cp().post(sum(digits, k));

    out.put("number", number);
  }
}
