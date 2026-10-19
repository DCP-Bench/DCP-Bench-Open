// Social golfers problem: golfers play once a week in groups of a given size,
// for a number of weeks, so that no two golfers share a group more than once.
// The instance gives n_groups, group_size and n_weeks; golfers = n_groups * group_size.
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int groups = inst.getInt("n_groups");
    int size = inst.getInt("group_size");
    int weeks = inst.getInt("n_weeks");
    int golfers = groups * size;

    // assign[i][j] is the group (0-based) of golfer i in week j
    CPIntVar[][] assign = new CPIntVar[golfers][weeks];
    for (int i = 0; i < golfers; i++)
      for (int j = 0; j < weeks; j++)
        assign[i][j] = m.intVar(0, groups - 1);

    // in[i][j][g] is 1 when golfer i plays in group g in week j
    CPBoolVar[][][] in = new CPBoolVar[golfers][weeks][groups];
    for (int i = 0; i < golfers; i++)
      for (int j = 0; j < weeks; j++)
        for (int g = 0; g < groups; g++)
          in[i][j][g] = isEq(assign[i][j], g);

    // every group holds exactly group_size golfers in every week
    for (int j = 0; j < weeks; j++)
      for (int g = 0; g < groups; g++) {
        CPBoolVar[] members = new CPBoolVar[golfers];
        for (int i = 0; i < golfers; i++)
          members[i] = in[i][j][g];
        m.cp().post(eq(sum(members), size));
      }

    // no two golfers play in the same group more than once:
    // together[j] is 1 exactly when the two golfers share a group in week j,
    // and the two golfers share a group in at most one week
    for (int a = 0; a < golfers; a++)
      for (int b = a + 1; b < golfers; b++) {
        CPBoolVar[] together = new CPBoolVar[weeks];
        for (int j = 0; j < weeks; j++) {
          CPBoolVar t = makeBoolVar(m.cp());
          together[j] = t;
          for (int g = 0; g < groups; g++) {
            // both in group g in week j means together
            m.cp().post(or(new CPBoolVar[]{not(in[a][j][g]), not(in[b][j][g]), t}));
            // together means both are in the same group g
            m.cp().post(or(new CPBoolVar[]{not(t), not(in[a][j][g]), in[b][j][g]}));
          }
        }
        m.cp().post(le(sum(together), 1));
      }

    out.put("assign", assign);
  }
}
