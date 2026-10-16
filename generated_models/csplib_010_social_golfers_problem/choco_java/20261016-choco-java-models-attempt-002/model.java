import org.chocosolver.solver.Model;
import org.chocosolver.solver.search.limits.FailCounter;
import org.chocosolver.solver.search.strategy.Search;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Social golfers: each week, split n_groups * group_size golfers into n_groups groups of group_size,
// so that no two golfers share a group on more than one occasion over n_weeks weeks.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int groups = inst.getInt("n_groups");
    int size = inst.getInt("group_size");
    int weeks = inst.getInt("n_weeks");
    int golfers = groups * size; // the club has exactly n_groups * group_size golfers

    // assign[i][w]: group of golfer i in week w
    IntVar[][] assign = m.intVarMatrix("assign", golfers, weeks, 0, groups - 1);

    int[] values = new int[groups];
    IntVar[] occurrences = new IntVar[groups];
    for (int g = 0; g < groups; g++) {
      values[g] = g;
      occurrences[g] = m.intVar(size);
    }

    // each golfer plays once a week, and every group holds exactly group_size golfers
    for (int w = 0; w < weeks; w++) {
      IntVar[] week = new IntVar[golfers];
      for (int i = 0; i < golfers; i++) week[i] = assign[i][w];
      m.globalCardinality(week, values, occurrences, true).post();
    }

    // the groups of a week are interchangeable: number them in order of first appearance
    // (symmetry breaking, it does not change which schedules exist)
    for (int w = 0; w < weeks; w++) {
      IntVar[] week = new IntVar[golfers];
      for (int i = 0; i < golfers; i++) week[i] = assign[i][w];
      m.intValuePrecedeChain(week, values).post();
    }

    // no two golfers play in the same group on more than one occasion
    for (int i = 0; i < golfers; i++) {
      for (int j = i + 1; j < golfers; j++) {
        BoolVar[] together = new BoolVar[weeks]; // together[w] = 1 if i and j share a group in week w
        for (int w = 0; w < weeks; w++) {
          together[w] = m.arithm(assign[i][w], "=", assign[j][w]).reify();
        }
        m.sum(together, "<=", 1).post();
      }
    }

    // search: most constrained variable first, with Luby restarts
    IntVar[] flat = new IntVar[golfers * weeks];
    for (int i = 0; i < golfers; i++)
      for (int w = 0; w < weeks; w++) flat[i * weeks + w] = assign[i][w];
    m.getSolver().setSearch(Search.domOverWDegSearch(flat));
    m.getSolver().setLubyRestart(50, new FailCounter(m, 1), 10000);

    out.put("assign", assign);
  }
}
