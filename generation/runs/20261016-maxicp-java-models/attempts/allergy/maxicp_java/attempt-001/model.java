// Four friends, Debra (0), Janet (1), Hugh (2) and Rick (3), each allergic to one of
// eggs, mold, nuts and ragweed, and each with one of the surnames Baxter, Lemon, Malone
// and Fleet. The outputs give, for each allergy and each surname, the friend it belongs to.
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // the friends are 0..3: Debra=0, Janet=1, Hugh=2, Rick=3
    CPIntVar eggs = m.intVar(0, 3);
    CPIntVar mold = m.intVar(0, 3);
    CPIntVar nuts = m.intVar(0, 3);
    CPIntVar ragweed = m.intVar(0, 3);

    CPIntVar baxter = m.intVar(0, 3);
    CPIntVar lemon = m.intVar(0, 3);
    CPIntVar malone = m.intVar(0, 3);
    CPIntVar fleet = m.intVar(0, 3);

    // each of the four friends has a different allergy
    m.cp().post(allDifferent(new CPIntVar[] {eggs, mold, nuts, ragweed}));
    // each of the four friends has a different surname
    m.cp().post(allDifferent(new CPIntVar[] {baxter, lemon, malone, fleet}));

    // Rick is not allergic to mold
    m.cp().post(neq(mold, 3));
    // Baxter is allergic to eggs
    m.cp().post(eq(baxter, eggs));
    // Hugh is neither surnamed Lemon nor Fleet
    m.cp().post(neq(lemon, 2));
    m.cp().post(neq(fleet, 2));
    // Debra is allergic to ragweed
    m.cp().post(eq(ragweed, 0));
    // Janet (who isn't Lemon) is neither allergic to eggs nor to mold
    m.cp().post(neq(lemon, 1));
    m.cp().post(neq(eggs, 1));
    m.cp().post(neq(mold, 1));

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
