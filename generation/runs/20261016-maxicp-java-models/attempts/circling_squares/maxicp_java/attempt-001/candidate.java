// Circling the squares: place a different whole number in each of the ten squares
// A, B, C, D, E, F, G, H, I, K around a circle, so that for any two adjacent
// numbers the sum of their squares equals the sum of the squares of the two
// numbers diametrically opposite them. Fractions are not allowed, and every
// number has at most two digits. The numbers A=16, B=2, F=8 and G=14 are fixed.
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // the ten squares in circle order: A B C D E F G H I K
    // every number is a whole number of at most two digits
    CPIntVar[] c = m.intVarArray(10, 0, 99);
    CPIntVar A = c[0], B = c[1], C = c[2], D = c[3], E = c[4];
    CPIntVar F = c[5], G = c[6], H = c[7], I = c[8], K = c[9];

    // a different number in each of the ten squares
    m.cp().post(allDifferent(c));

    // the squares of every number, looked up from a table of k*k for k = 0..99
    int[] square = new int[100];
    for (int k = 0; k < 100; k++) {
      square[k] = k * k;
    }
    CPIntVar[] sq = new CPIntVar[10];
    for (int i = 0; i < 10; i++) {
      sq[i] = element(square, c[i]);
    }

    // the sum of the squares of any two adjacent numbers equals the sum of the squares
    // of the two numbers diametrically opposite them, for every pair of adjacent squares
    for (int i = 0; i < 10; i++) {
      int j = (i + 1) % 10;
      int opposite1 = (i + 5) % 10;
      int opposite2 = (i + 6) % 10;
      m.cp().post(eq(sum(sq[i], sq[j]), sum(sq[opposite1], sq[opposite2])));
    }

    // the given numbers: A = 16, B = 2, F = 8, G = 14
    m.cp().post(eq(A, 16));
    m.cp().post(eq(B, 2));
    m.cp().post(eq(F, 8));
    m.cp().post(eq(G, 14));

    out.put("A", A);
    out.put("B", B);
    out.put("C", C);
    out.put("D", D);
    out.put("E", E);
    out.put("F", F);
    out.put("G", G);
    out.put("H", H);
    out.put("I", I);
    out.put("K", K);
  }
}
