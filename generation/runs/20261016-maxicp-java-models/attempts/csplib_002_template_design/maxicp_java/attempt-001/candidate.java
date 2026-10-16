import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Template design: choose how many templates to make, which variations go on
// each template and how many copies of each, and how many sheets to print from
// each template, so that every variation's order is met and the number of
// printed sheets is as small as possible.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int slots = inst.getInt("n_slots");          // variations that fit on one template
    int templates = inst.getInt("n_templates");  // number of templates to produce
    int variations = inst.getInt("n_var");       // number of distinct variations
    int[] demand = inst.getIntArray("demand");   // copies ordered of each variation

    int totalDemand = 0;
    for (int d : demand) {
      totalDemand += d;
    }

    // layout[t][v] = number of copies of variation v on template t
    CPIntVar[][] layout = new CPIntVar[templates][];
    for (int t = 0; t < templates; t++) {
      // no template needs more copies of a variation than are ordered
      layout[t] = new CPIntVar[variations];
      for (int v = 0; v < variations; v++) {
        layout[t][v] = m.intVar(0, Math.min(slots, demand[v]));
      }
    }

    // production[t] = number of sheets printed from template t
    CPIntVar[] production = m.intVarArray(templates, 0, totalDemand);

    // each template holds at most as many copies as there are slots on it
    for (int t = 0; t < templates; t++) {
      m.cp().post(le(sum(layout[t]), slots));
    }

    // the copies printed for each variation (sheets times copies per sheet, summed
    // over the templates) cover the ordered quantity of that variation
    for (int v = 0; v < variations; v++) {
      CPIntVar[] printed = new CPIntVar[templates];
      for (int t = 0; t < templates; t++) {
        printed[t] = mul(production[t], layout[t][v]);
      }
      m.cp().post(ge(sum(printed), demand[v]));
    }

    // implied by the two rules above: a sheet carries at most n_slots copies, so the
    // printed sheets in total must carry at least the total demand
    m.cp().post(ge(mul(sum(production), slots), totalDemand));

    // minimise the total number of printed sheets
    m.minimize(sum(production));

    out.put("layout", layout);
    out.put("production", production);
  }
}
