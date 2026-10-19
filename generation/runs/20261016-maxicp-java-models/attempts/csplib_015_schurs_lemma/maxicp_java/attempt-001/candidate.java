// Schur's lemma: put balls 1..n into boxes so that no triple of balls
// (x, y, z) with x + y = z lies entirely in one box.
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");
    int boxes = inst.getInt("c");

    // every ball is in exactly one box, numbered 1..boxes
    CPIntVar[] balls = m.intVarArray(n, 1, boxes);

    // inBox[i][j] is true when ball i+1 is in box j+1
    CPBoolVar[][] inBox = new CPBoolVar[n][boxes];
    for (int i = 0; i < n; i++) {
      for (int j = 0; j < boxes; j++) {
        inBox[i][j] = isEq(balls[i], j + 1);
      }
    }

    // for any triple of balls x + y = z, not all three are in the same box
    for (int x = 1; x <= n; x++) {
      for (int y = x; y <= n; y++) {
        int z = x + y;
        if (z > n) break;
        for (int j = 0; j < boxes; j++) {
          if (x == y) {
            // the triple has only two distinct balls: x and z
            m.cp().post(or(new CPBoolVar[] { not(inBox[x - 1][j]), not(inBox[z - 1][j]) }));
          } else {
            m.cp().post(or(new CPBoolVar[] {
                not(inBox[x - 1][j]), not(inBox[y - 1][j]), not(inBox[z - 1][j]) }));
          }
        }
      }
    }

    out.put("balls", balls);
  }
}
