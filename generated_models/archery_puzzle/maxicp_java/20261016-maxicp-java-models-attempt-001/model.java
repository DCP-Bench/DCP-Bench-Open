import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Archery: a young archer shoots arrows at six targets, each target with its own score.
// She may shoot as many arrows as she likes. Find the number of hits on each target
// so that the total score is as close as possible to the target score.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[] targets = inst.getIntArray("targets");
    int target = inst.getInt("target_score");
    int n = targets.length;

    int maxTarget = 0;
    for (int t : targets) maxTarget = Math.max(maxTarget, t);

    // A total more than maxTarget above the target can be lowered by removing one
    // arrow, so no optimal solution goes past target + maxTarget. This bounds the hits.
    int totalBound = target + maxTarget;

    // the number of hits on each target
    CPIntVar[] hits = new CPIntVar[n];
    for (int i = 0; i < n; i++) {
      hits[i] = m.intVar(0, totalBound / targets[i]);
    }

    // each hit on a target scores the points of that target
    CPIntVar[] scores = new CPIntVar[n];
    for (int i = 0; i < n; i++) {
      scores[i] = mul(hits[i], targets[i]);
    }

    // the total score of all arrows
    CPIntVar total = sum(scores);

    // the distance between the total score and the target score
    CPIntVar diff = minus(total, target);

    // the deviation is the absolute value of the difference
    CPIntVar deviation = m.intVar(0, totalBound);
    m.cp().post(ge(deviation, diff));
    m.cp().post(ge(deviation, minus(diff)));

    // minimise how far the total score is from the target score
    m.minimize(deviation);

    out.put("hits", hits);
  }
}
