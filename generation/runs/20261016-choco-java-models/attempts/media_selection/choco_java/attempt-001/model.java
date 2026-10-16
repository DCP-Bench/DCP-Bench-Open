import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
import java.util.ArrayList;
import java.util.List;
import dcp.Instance;
import dcp.Outputs;

// Media selection: choose advertising media so that every target audience is reached by
// at least one selected medium, at minimum total campaign cost.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[][] incidence = inst.getIntMatrix("incidence_matrix");  // incidence[audience][medium] = 1 if the medium reaches the audience
    int[] costs = inst.getIntArray("media_costs");
    int audiences = incidence.length, media = costs.length;

    // is_selected[j] = 1 if medium j is bought
    BoolVar[] selected = m.boolVarArray("selected", media);

    // every audience is reached by at least one selected medium
    for (int a = 0; a < audiences; a++) {
      List<BoolVar> reaching = new ArrayList<>();
      for (int j = 0; j < media; j++) if (incidence[a][j] == 1) reaching.add(selected[j]);
      m.sum(reaching.toArray(new BoolVar[0]), ">=", 1).post();
    }

    // total campaign cost: the costs of the selected media
    int maxCost = 0;
    for (int c : costs) maxCost += c;
    IntVar total = m.intVar("total", 0, maxCost, true);
    m.scalar(selected, costs, "=", total).post();

    // spend no more than necessary
    m.setObjective(Model.MINIMIZE, total);

    out.put("is_selected", selected);
    out.put("min_total_cost", total);
  }
}
