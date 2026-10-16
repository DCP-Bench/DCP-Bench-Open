// Added corners: place the digits 1 through 8 in the four circles (corners) and
// four squares (edge cells) of a 3x3 frame so that each square equals the sum of
// the two adjoining circles.
import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // positions in reading order: TL, TM, TR, ML, MR, BL, BM, BR
    IntVar[] p = m.intVarArray("positions", 8, 1, 8);
    IntVar tl = p[0], tm = p[1], tr = p[2], ml = p[3], mr = p[4], bl = p[5], bm = p[6], br = p[7];

    // enter the digits 1 through 8, each once
    m.allDifferent(p, "AC").post();

    // top square equals the sum of the two top circles
    tl.add(tr).eq(tm).post();

    // middle-left square equals the sum of the top-left and bottom-left circles
    tl.add(bl).eq(ml).post();

    // middle-right square equals the sum of the top-right and bottom-right circles
    tr.add(br).eq(mr).post();

    // bottom square equals the sum of the two bottom circles
    bl.add(br).eq(bm).post();

    out.put("positions", p);
  }
}
