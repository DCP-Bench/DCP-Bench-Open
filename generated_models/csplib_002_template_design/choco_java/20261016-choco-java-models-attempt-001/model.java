import org.chocosolver.solver.Model;
import org.chocosolver.solver.search.limits.FailCounter;
import org.chocosolver.solver.search.strategy.Search;
import org.chocosolver.util.tools.ArrayUtils;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Template design: print each variation's demand from a few templates, each template
// carrying at most n_slots variations, and minimise the total number of printed sheets.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int nSlots = inst.getInt("n_slots");
    int nTemplates = inst.getInt("n_templates");
    int nVar = inst.getInt("n_var");
    int[] demand = inst.getIntArray("demand");

    // the largest demand bounds how many sheets any one template can need
    int maxDemand = 0;
    for (int d : demand) maxDemand = Math.max(maxDemand, d);

    // layout[t][v]: copies of variation v etched on template t
    IntVar[][] layout = m.intVarMatrix("layout", nTemplates, nVar, 0, nSlots);
    // production[t]: number of sheets printed from template t
    IntVar[] production = m.intVarArray("production", nTemplates, 0, maxDemand);

    // each template holds at most n_slots variations
    for (int t = 0; t < nTemplates; t++)
      m.sum(layout[t], "<=", nSlots).post();

    // every variation's demand is at least met by the sheets printed from all templates together
    // (contribution of template t to variation v is layout[t][v] * production[t])
    for (int v = 0; v < nVar; v++) {
      IntVar[] contributions = new IntVar[nTemplates];
      for (int t = 0; t < nTemplates; t++) {
        contributions[t] = m.intVar(0, nSlots * maxDemand);
        m.times(layout[t][v], production[t], contributions[t]).post();
      }
      m.sum(contributions, ">=", demand[v]).post();
    }

    // implied bound: a sheet carries at most n_slots variations, so the sheets printed
    // must cover the total demand at that rate (rounded up)
    int totalDemand = 0;
    for (int d : demand) totalDemand += d;
    int sheetsLowerBound = (totalDemand + nSlots - 1) / nSlots;

    // minimise the total number of printed sheets
    IntVar totalSheets = m.sum("totalSheets", production);
    m.arithm(totalSheets, ">=", sheetsLowerBound).post();
    m.setObjective(Model.MINIMIZE, totalSheets);

    // symmetry breaking: templates are interchangeable, so list them by decreasing production
    for (int t = 0; t + 1 < nTemplates; t++)
      m.arithm(production[t], ">=", production[t + 1]).post();

    // branch on the variations etched on each template first, then on the sheet counts,
    // with dom/wdeg and Luby restarts
    IntVar[] flatLayout = new IntVar[nTemplates * nVar];
    for (int t = 0; t < nTemplates; t++)
      for (int v = 0; v < nVar; v++)
        flatLayout[t * nVar + v] = layout[t][v];
    m.getSolver().setSearch(
        Search.domOverWDegSearch(flatLayout),
        Search.inputOrderLBSearch(production));
    m.getSolver().setLubyRestart(50, new FailCounter(m, 1), 10000);

    out.put("layout", layout);
    out.put("production", production);
  }
}
