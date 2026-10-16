import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Archery: the archer shoots as many arrows as she likes at targets whose rings score
// targets[i] each. Choose the number of hits on each target so that the total score
// comes as close as possible to target_score.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[] ring = inst.getIntArray("targets");
    int goal = inst.getInt("target_score");
    int k = ring.length;

    // zero arrows miss the goal by goal, so the best total is at most 2 * goal; this caps the hits
    int cap = 2 * goal;
    IntVar[] hits = new IntVar[k];
    for (int i = 0; i < k; i++) {
      hits[i] = m.intVar("hits_" + i, 0, cap / ring[i]);
    }

    // total score: each hit on target i scores ring[i]
    IntVar total = m.intVar("total", 0, cap, true);
    m.scalar(hits, ring, "=", total).post();

    // distance from the target score: deviation = |total - target_score|
    IntVar diff = m.intVar("diff", -cap, cap, true);
    m.arithm(diff, "=", total, "-", goal).post();
    IntVar deviation = m.intVar("deviation", 0, cap, true);
    m.absolute(deviation, diff).post();

    // get as close to the target score as possible
    m.setObjective(Model.MINIMIZE, deviation);

    out.put("hits", hits);
  }
}
