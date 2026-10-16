import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Harriet bought four pairs of shoes at four stores, one stop each (stops 1 to 4).
// Work out the order of the stops, which shoe and which store at each stop.
// Values are the stop numbers, 1 to 4; the same value denotes the same shoe or store.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // the four shoes and the four stores, each takes the stop numbers 1 to 4
    CPIntVar ecru = m.intVar(1, 4);
    CPIntVar fuchsia = m.intVar(1, 4);
    CPIntVar purple = m.intVar(1, 4);
    CPIntVar suede = m.intVar(1, 4);
    CPIntVar footFarm = m.intVar(1, 4);
    CPIntVar heels = m.intVar(1, 4);
    CPIntVar shoePalace = m.intVar(1, 4);
    CPIntVar tootsies = m.intVar(1, 4);

    // each stop has a different shoe
    m.cp().post(allDifferent(new CPIntVar[] {ecru, fuchsia, purple, suede}));
    // each stop has a different store
    m.cp().post(allDifferent(new CPIntVar[] {footFarm, heels, shoePalace, tootsies}));

    // Harriet bought fuchsia flats at Heels in a Handcart
    m.cp().post(eq(fuchsia, heels));
    // The store she visited just after buying her purple pumps was not Tootsies
    m.cp().post(neq(tootsies, plus(purple, 1)));
    // The Foot Farm was Harriet's second stop
    m.cp().post(eq(footFarm, 2));
    // Two stops after leaving The Shoe Palace, Harriet bought her suede sandals
    m.cp().post(eq(suede, plus(shoePalace, 2)));

    out.put("ecruespadrilles", ecru);
    out.put("footfarm", footFarm);
    out.put("fuchsiaflats", fuchsia);
    out.put("heelsinahandcart", heels);
    out.put("purplepumps", purple);
    out.put("suedesandals", suede);
    out.put("theshoepalace", shoePalace);
    out.put("tootsies", tootsies);
  }
}
