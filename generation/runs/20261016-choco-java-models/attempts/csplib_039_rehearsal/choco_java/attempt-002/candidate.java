import java.util.ArrayList;
import java.util.List;
import org.chocosolver.solver.Model;
import org.chocosolver.solver.search.strategy.Search;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Rehearsal: order the pieces of a concert so that the total time players spend waiting
// (present at rehearsal but not playing) is as small as possible.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("num_pieces");
    int np = inst.getInt("num_players");
    int[] dur = inst.getIntArray("duration");
    int[][] rehearsal = inst.getIntMatrix("rehearsal");  // rehearsal[p][j] = 1 if player p plays piece j
    int horizon = 0;
    for (int d : dur) horizon += d;

    // start[j]: time at which piece j starts; end[j] = start[j] + duration of piece j
    IntVar[] start = m.intVarArray("start", n, 0, horizon, true);
    IntVar[] end = new IntVar[n];
    for (int j = 0; j < n; j++) end[j] = m.offset(start[j], dur[j]);

    // pieces are rehearsed one after another, never at the same time
    for (int i = 0; i < n; i++) {
      for (int j = i + 1; j < n; j++) {
        m.or(m.arithm(end[i], "<=", start[j]), m.arithm(end[j], "<=", start[i])).post();
      }
    }

    // pos[j]: the slot of piece j, i.e. how many pieces are rehearsed before it
    IntVar[] pos = new IntVar[n];
    for (int j = 0; j < n; j++) {
      BoolVar[] before = new BoolVar[n - 1];
      int k = 0;
      for (int i = 0; i < n; i++) {
        if (i != j) before[k++] = m.arithm(start[i], "<", start[j]).reify();
      }
      pos[j] = m.sum("pos" + j, before);
    }
    // order[s]: the piece rehearsed in slot s (the rehearsal order)
    IntVar[] order = m.intVarArray("order", n, 0, n - 1);
    m.inverseChanneling(pos, order).post();

    // waiting time of each player: from the start of the first piece he plays
    // to the end of the last one, minus the time he actually plays
    List<IntVar> waits = new ArrayList<>();
    for (int p = 0; p < np; p++) {
      List<IntVar> firstStarts = new ArrayList<>();
      List<IntVar> lastEnds = new ArrayList<>();
      int playing = 0;
      for (int j = 0; j < n; j++) {
        if (rehearsal[p][j] == 1) {
          firstStarts.add(start[j]);
          lastEnds.add(end[j]);
          playing += dur[j];
        }
      }
      if (firstStarts.isEmpty()) continue;
      IntVar first = m.min("first" + p, firstStarts.toArray(new IntVar[0]));
      IntVar last = m.max("last" + p, lastEnds.toArray(new IntVar[0]));
      IntVar present = m.intVar("present" + p, 0, horizon, true);
      m.arithm(present, "=", last, "-", first).post();
      waits.add(m.offset(present, -playing));
    }

    // branch on start times, earliest-possible piece first, so schedules are built in sequence
    m.getSolver().setSearch(Search.minDomLBSearch(start));

    // minimise the total waiting time over all players
    IntVar total = m.sum("total", waits.toArray(new IntVar[0]));
    m.setObjective(Model.MINIMIZE, total);

    out.put("rehearsal_order", order);
  }
}
