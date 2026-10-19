// N fractions puzzle: find distinct non-zero digits A..I such that
// A/BC + D/EF + G/HI = 1, where BC, EF and HI are two-digit numbers.
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // the nine digits are distinct and non-zero
    CPIntVar A = m.intVar(1, 9);
    CPIntVar B = m.intVar(1, 9);
    CPIntVar C = m.intVar(1, 9);
    CPIntVar D = m.intVar(1, 9);
    CPIntVar E = m.intVar(1, 9);
    CPIntVar F = m.intVar(1, 9);
    CPIntVar G = m.intVar(1, 9);
    CPIntVar H = m.intVar(1, 9);
    CPIntVar I = m.intVar(1, 9);
    m.cp().post(allDifferent(new CPIntVar[] {A, B, C, D, E, F, G, H, I}));

    // BC, EF and HI are the two-digit numbers formed by their digits
    CPIntVar bc = sum(new CPIntVar[] {mul(B, 10), C});
    CPIntVar ef = sum(new CPIntVar[] {mul(E, 10), F});
    CPIntVar hi = sum(new CPIntVar[] {mul(H, 10), I});

    // A/BC + D/EF + G/HI = 1, multiplied through by BC*EF*HI so that no division is needed:
    // A*EF*HI + D*BC*HI + G*BC*EF = BC*EF*HI
    CPIntVar efhi = mul(ef, hi);
    CPIntVar bchi = mul(bc, hi);
    CPIntVar bcef = mul(bc, ef);
    CPIntVar product = mul(bc, efhi);
    // the three fractions add up to one
    m.cp().post(eq(sum(new CPIntVar[] {mul(A, efhi), mul(D, bchi), mul(G, bcef)}), product));

    out.put("A", A);
    out.put("B", B);
    out.put("C", C);
    out.put("D", D);
    out.put("E", E);
    out.put("F", F);
    out.put("G", G);
    out.put("H", H);
    out.put("I", I);
  }
}
