import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Circling squares: ten numbers on a circle, all different, such that for any two adjacent
// numbers the sum of their squares equals the sum of the squares of the two diametrically opposite numbers.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // the ten squares in circle order: A B C D E F G H I K
    IntVar[] p = m.intVarArray("p", 10, 1, 99);
    IntVar A = p[0], B = p[1], C = p[2], D = p[3], E = p[4], F = p[5], G = p[6], H = p[7], I = p[8], K = p[9];

    // every square holds a different number
    m.allDifferent(p, "AC").post();

    // squares of the circle
    IntVar[] sq = new IntVar[10];
    for (int i = 0; i < 10; i++) sq[i] = p[i].mul(p[i]).intVar();

    // adjacent pair and its diametrically opposite pair have equal sums of squares
    int[] coef = {1, 1, -1, -1};
    for (int i = 0; i < 5; i++) {
      IntVar[] vs = {sq[i], sq[(i + 1) % 10], sq[(i + 5) % 10], sq[(i + 6) % 10]};
      m.scalar(vs, coef, "=", 0).post();
    }

    // the four numbers given in the description
    m.arithm(A, "=", 16).post();
    m.arithm(B, "=", 2).post();
    m.arithm(F, "=", 8).post();
    m.arithm(G, "=", 14).post();

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
