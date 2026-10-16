// Media selection: choose which advertising media to buy so that every target
// audience is reached by at least one bought medium, at minimum total campaign cost.
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // incidence[a][j] = 1 if medium j reaches audience a (rows are audiences, columns are media)
    int[][] incidence = inst.getIntMatrix("incidence_matrix");
    // media_costs[j] = cost of buying medium j
    int[] mediaCosts = inst.getIntArray("media_costs");
    int nAudiences = incidence.length;
    int nMedia = mediaCosts.length;

    // is_selected[j] = 1 if medium j is bought
    CPBoolVar[] isSelected = m.boolVarArray(nMedia);

    // every target audience is reached at least once by a selected medium
    for (int a = 0; a < nAudiences; a++) {
      int count = 0;
      for (int j = 0; j < nMedia; j++) if (incidence[a][j] == 1) count++;
      CPBoolVar[] reachingMedia = new CPBoolVar[count];
      int k = 0;
      for (int j = 0; j < nMedia; j++) if (incidence[a][j] == 1) reachingMedia[k++] = isSelected[j];
      m.cp().post(or(reachingMedia));
    }

    // total campaign cost is the sum of the costs of the selected media
    int sumCosts = 0;
    for (int c : mediaCosts) sumCosts += c;
    CPIntVar[] costTerms = new CPIntVar[nMedia];
    for (int j = 0; j < nMedia; j++) costTerms[j] = mul(isSelected[j], mediaCosts[j]);
    CPIntVar totalCost = m.intVar(0, sumCosts);
    m.cp().post(eq(totalCost, sum(costTerms)));

    // the campaign should cost no more than necessary
    m.minimize(totalCost);

    out.put("is_selected", isSelected);
    out.put("min_total_cost", totalCost);
  }
}
