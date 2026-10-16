import java.util.ArrayList;
import java.util.List;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Seat six guests around a round table so that no two guests who do not get along sit next to each other.
// Guests: 0 Andrew, 1 Betty, 2 Cara, 3 Dave, 4 Erica, 5 Frank.
// The problem has no instance data, so the model reads nothing from the instance.
public class Submission {

  static final int ANDREW = 0, BETTY = 1, CARA = 2, DAVE = 3, ERICA = 4, FRANK = 5;

  public static void build(Instance inst, Model m, Outputs out) {
    // x[p] is the guest in seat p, seats 0..5 in order around the table.
    CPIntVar[] x = m.intVarArray(6, 0, 5);

    // each guest sits in exactly one seat
    m.cp().post(allDifferent(x));

    // the pairs of guests who will sit next to each other, in both orders
    // Andrew will only sit next to Dave and Frank
    // Betty will only sit next to Cara and Erica
    // Cara will only sit next to Betty and Frank
    // Dave will only sit next to Andrew and Erica
    // Erica will only sit next to Betty and Dave
    // Frank will only sit next to Andrew and Cara
    int[][] allowed = {
      {ANDREW, DAVE}, {DAVE, ANDREW}, {ANDREW, FRANK}, {FRANK, ANDREW},
      {BETTY, CARA}, {CARA, BETTY}, {BETTY, ERICA}, {ERICA, BETTY},
      {CARA, FRANK}, {FRANK, CARA},
      {DAVE, ERICA}, {ERICA, DAVE}
    };

    // every guest sits next to only guests they get along with, including the
    // seats at the two ends, since the table is round
    for (int p = 0; p < 6; p++) {
      m.cp().post(table(new CPIntVar[]{x[p], x[(p + 1) % 6]}, allowed));
    }

    out.put("x", x);
  }
}
