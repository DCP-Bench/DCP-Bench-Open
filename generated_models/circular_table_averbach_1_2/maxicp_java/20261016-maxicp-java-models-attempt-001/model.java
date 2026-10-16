// Circular table (Averbach 1-2): three players X, Y, Z of nationalities American, English and
// French sit around a circular table playing Hearts. Seats are 0, 1, 2; 1 is right of 0, 2 is
// right of 1, and 0 is right of 2. Each player passed three cards to the person on their right.
// Outputs: x, y, z are the seats of X, Y, Z; american, english, french are the seats of the
// players of each nationality.
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // the seats are 0, 1, 2 around the table (a fixed property of the problem)
    CPIntVar x = m.intVar(0, 2);
    CPIntVar y = m.intVar(0, 2);
    CPIntVar z = m.intVar(0, 2);
    CPIntVar american = m.intVar(0, 2);
    CPIntVar english = m.intVar(0, 2);
    CPIntVar french = m.intVar(0, 2);

    // X, Y and Z sit in three different seats
    m.cp().post(allDifferent(new CPIntVar[] {x, y, z}));

    // the American, the English and the French are three different people
    m.cp().post(allDifferent(new CPIntVar[] {american, english, french}));

    // the person on the right of seat s is (s + 1) mod 3
    CPIntVar rightOfY = element(new int[] {1, 2, 0}, y);
    // Y passed three hearts to the American: the American is on Y's right
    m.cp().post(eq(american, rightOfY));

    // X passed the queen of spades and two diamonds to the person who passed their cards to the
    // Frenchwoman. X's right neighbour is that passer, and the passer's right neighbour is the
    // Frenchwoman, so the Frenchwoman sits at seat (x + 2) mod 3.
    CPIntVar frenchSeat = element(new int[] {2, 0, 1}, x);
    m.cp().post(eq(french, frenchSeat));

    out.put("x", x);
    out.put("y", y);
    out.put("z", z);
    out.put("american", american);
    out.put("english", english);
    out.put("french", french);
  }
}
