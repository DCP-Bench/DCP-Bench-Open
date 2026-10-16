import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Find distinct non-zero digits A..I such that A/BC + D/EF + G/HI = 1, where BC, EF and HI
// are the two-digit numbers 10B+C, 10E+F and 10H+I.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    IntVar A = m.intVar("A", 1, 9);
    IntVar B = m.intVar("B", 1, 9);
    IntVar C = m.intVar("C", 1, 9);
    IntVar D = m.intVar("D", 1, 9);
    IntVar E = m.intVar("E", 1, 9);
    IntVar F = m.intVar("F", 1, 9);
    IntVar G = m.intVar("G", 1, 9);
    IntVar H = m.intVar("H", 1, 9);
    IntVar I = m.intVar("I", 1, 9);

    // the digits are distinct and non-zero: nine different values from 1..9
    m.allDifferent(new IntVar[]{A, B, C, D, E, F, G, H, I}, "AC").post();

    // BC, EF and HI are the two-digit numbers formed by their digits
    IntVar BC = m.intVar("BC", 10, 99);
    IntVar EF = m.intVar("EF", 10, 99);
    IntVar HI = m.intVar("HI", 10, 99);
    m.scalar(new IntVar[]{B, C}, new int[]{10, 1}, "=", BC).post();
    m.scalar(new IntVar[]{E, F}, new int[]{10, 1}, "=", EF).post();
    m.scalar(new IntVar[]{H, I}, new int[]{10, 1}, "=", HI).post();

    // A/BC + D/EF + G/HI = 1, multiplied through by BC*EF*HI to avoid fractions:
    // A*EF*HI + D*BC*HI + G*BC*EF = BC*EF*HI
    IntVar efHi = m.intVar("EF*HI", 100, 99 * 99, true);
    IntVar bcHi = m.intVar("BC*HI", 100, 99 * 99, true);
    IntVar bcEf = m.intVar("BC*EF", 100, 99 * 99, true);
    IntVar bcEfHi = m.intVar("BC*EF*HI", 1000, 99 * 99 * 99, true);
    m.times(EF, HI, efHi).post();
    m.times(BC, HI, bcHi).post();
    m.times(BC, EF, bcEf).post();
    m.times(bcEf, HI, bcEfHi).post();

    IntVar termA = m.intVar("A*EF*HI", 0, 9 * 99 * 99, true);
    IntVar termD = m.intVar("D*BC*HI", 0, 9 * 99 * 99, true);
    IntVar termG = m.intVar("G*BC*EF", 0, 9 * 99 * 99, true);
    m.times(A, efHi, termA).post();
    m.times(D, bcHi, termD).post();
    m.times(G, bcEf, termG).post();

    m.sum(new IntVar[]{termA, termD, termG}, "=", bcEfHi).post();

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
