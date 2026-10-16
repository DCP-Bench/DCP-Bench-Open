import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Four friends (Debra=0, Janet=1, Hugh=2, Rick=3) each have a different surname
// (Baxter, Lemon, Malone, Fleet) and a different allergy (eggs, mold, nuts, ragweed).
// Find the friend index for each surname and each allergy.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // Friend indices from the statement: Debra=0, Janet=1, Hugh=2, Rick=3.
    final int DEBRA = 0, JANET = 1, HUGH = 2, RICK = 3;

    IntVar baxter = m.intVar("baxter", 0, 3);
    IntVar lemon = m.intVar("lemon", 0, 3);
    IntVar malone = m.intVar("malone", 0, 3);
    IntVar fleet = m.intVar("fleet", 0, 3);
    IntVar eggs = m.intVar("eggs", 0, 3);
    IntVar mold = m.intVar("mold", 0, 3);
    IntVar nuts = m.intVar("nuts", 0, 3);
    IntVar ragweed = m.intVar("ragweed", 0, 3);

    // each friend has a different surname
    m.allDifferent(new IntVar[]{baxter, lemon, malone, fleet}, "AC").post();

    // each friend has a different allergy
    m.allDifferent(new IntVar[]{eggs, mold, nuts, ragweed}, "AC").post();

    // Baxter is allergic to eggs
    baxter.eq(eggs).post();

    // Rick is not allergic to mold
    mold.ne(RICK).post();

    // Hugh is neither surnamed Lemon nor Fleet
    lemon.ne(HUGH).post();
    fleet.ne(HUGH).post();

    // Debra is allergic to ragweed
    ragweed.eq(DEBRA).post();

    // Janet (who isn't Lemon) is neither allergic to eggs nor to mold
    lemon.ne(JANET).post();
    eggs.ne(JANET).post();
    mold.ne(JANET).post();

    out.put("baxter", baxter);
    out.put("eggs", eggs);
    out.put("fleet", fleet);
    out.put("lemon", lemon);
    out.put("malone", malone);
    out.put("mold", mold);
    out.put("nuts", nuts);
    out.put("ragweed", ragweed);
  }
}
