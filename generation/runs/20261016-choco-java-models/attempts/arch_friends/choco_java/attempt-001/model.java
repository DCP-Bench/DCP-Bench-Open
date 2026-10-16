import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Shoe shopping: four shoes and four stores, each bought at a distinct stop 1..4;
// find the stop of every shoe and every store that satisfy the four clues.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // stop number of each shoe
    IntVar ecru = m.intVar("ecruespadrilles", 1, 4);
    IntVar fuchsia = m.intVar("fuchsiaflats", 1, 4);
    IntVar purple = m.intVar("purplepumps", 1, 4);
    IntVar suede = m.intVar("suedesandals", 1, 4);
    // stop number of each store
    IntVar footFarm = m.intVar("footfarm", 1, 4);
    IntVar heels = m.intVar("heelsinahandcart", 1, 4);
    IntVar palace = m.intVar("theshoepalace", 1, 4);
    IntVar tootsies = m.intVar("tootsies", 1, 4);

    // each stop holds exactly one shoe kind
    m.allDifferent(new IntVar[]{ecru, fuchsia, purple, suede}, "AC").post();
    // each stop is exactly one store
    m.allDifferent(new IntVar[]{footFarm, heels, palace, tootsies}, "AC").post();

    // Harriet bought fuchsia flats at Heels in a Handcart
    m.arithm(fuchsia, "=", heels).post();

    // the store visited just after buying her purple pumps was not Tootsies
    m.arithm(tootsies, "-", purple, "!=", 1).post();

    // The Foot Farm was Harriet's second stop
    m.arithm(footFarm, "=", 2).post();

    // two stops after leaving The Shoe Palace, Harriet bought her suede sandals
    m.arithm(suede, "-", palace, "=", 2).post();

    out.put("ecruespadrilles", ecru);
    out.put("fuchsiaflats", fuchsia);
    out.put("purplepumps", purple);
    out.put("suedesandals", suede);
    out.put("footfarm", footFarm);
    out.put("heelsinahandcart", heels);
    out.put("theshoepalace", palace);
    out.put("tootsies", tootsies);
  }
}
