import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Robbery at Sparkles the Jeweller's: six suspects, each guilty (1) or innocent (0).
// Guilty suspects lie and innocent ones tell the truth, so each suspect's statement
// is true exactly when that suspect is innocent.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    CPBoolVar artie = m.boolVar();
    CPBoolVar bill = m.boolVar();
    CPBoolVar crackitt = m.boolVar();
    CPBoolVar dodgy = m.boolVar();
    CPBoolVar edgy = m.boolVar();
    CPBoolVar fingers = m.boolVar();
    CPIntVar[] guilty = {artie, bill, crackitt, dodgy, edgy, fingers};

    // the getaway car was barely big enough to hold two, so at least four are innocent
    m.cp().post(le(sum(guilty), 2));

    // Artie: "It wasn't me." Artie is innocent exactly when his statement is true,
    // which holds for either value of artie, so this adds no constraint.

    // Bill: "Crackitt was in it up to his neck." Bill is innocent exactly when
    // Crackitt is guilty.
    m.cp().post(eq(bill, not(crackitt)));

    // Crackitt: "No I wasn't." Crackitt is innocent exactly when his statement is true,
    // which holds for either value of crackitt, so this adds no constraint.

    // Dodgy: "If Crackitt did it, Bill did it with him." The statement is
    // (crackitt implies bill), so Dodgy is guilty exactly when crackitt is true and
    // bill is false. Written as three clauses:
    m.cp().post(or(new CPBoolVar[] {not(dodgy), crackitt}));          // dodgy implies crackitt
    m.cp().post(or(new CPBoolVar[] {not(dodgy), not(bill)}));         // dodgy implies not bill
    m.cp().post(or(new CPBoolVar[] {not(crackitt), bill, dodgy}));    // crackitt and not bill imply dodgy

    // Edgy: "Nobody did it alone." The statement is false exactly when one person
    // did it alone, so Edgy is guilty exactly when the number of guilty suspects is 1.
    m.cp().post(eq(edgy, isEq(sum(guilty), 1)));

    // Fingers: "That's right: it was Artie and Dodgy together." The statement is true
    // exactly when the guilty set is {Artie, Dodgy}, i.e. the weighted sum with
    // weights artie=1, bill=2, crackitt=4, dodgy=8, edgy=16, fingers=32 equals 1 + 8 = 9.
    // Fingers is guilty exactly when that statement is false.
    CPIntVar[] weighted = {artie, mul(bill, 2), mul(crackitt, 4), mul(dodgy, 8), mul(edgy, 16), mul(fingers, 32)};
    m.cp().post(eq(fingers, not(isEq(sum(weighted), 9))));

    out.put("artie", artie);
    out.put("bill", bill);
    out.put("crackitt", crackitt);
    out.put("dodgy", dodgy);
    out.put("edgy", edgy);
    out.put("fingers", fingers);
  }
}
