import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Six suspects of a robbery, who of them is guilty: the innocent ones tell the truth,
// the guilty ones lie, and the getaway car held at most two people.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // one 0/1 variable per suspect: 1 = guilty, 0 = innocent (order as in the description)
    BoolVar artie = m.boolVar("artie");
    BoolVar bill = m.boolVar("bill");
    BoolVar crackitt = m.boolVar("crackitt");
    BoolVar dodgy = m.boolVar("dodgy");
    BoolVar edgy = m.boolVar("edgy");
    BoolVar fingers = m.boolVar("fingers");
    BoolVar[] guilty = {artie, bill, crackitt, dodgy, edgy, fingers};

    // the getaway car was barely big enough to hold two, so at most two are guilty
    IntVar guiltyCount = m.sum("guilty count", guilty);
    guiltyCount.le(2).post();

    // a suspect's statement is true exactly when the suspect is innocent
    // "It wasn't me." (Artie)
    BoolVar artieSays = artie.not();
    m.arithm(artieSays, "!=", artie).post();

    // "Crackitt was in it up to his neck." (Bill)
    m.arithm(crackitt, "!=", bill).post();

    // "No I wasn't." (Crackitt)
    BoolVar crackittSays = crackitt.not();
    m.arithm(crackittSays, "!=", crackitt).post();

    // "If Crackitt did it, Bill did it with him." (Dodgy)
    BoolVar dodgySays = crackitt.eq(1).imp(bill.eq(1)).boolVar();
    m.arithm(dodgySays, "!=", dodgy).post();

    // "Nobody did it alone." (Edgy): the number of guilty is not exactly one
    BoolVar edgySays = guiltyCount.ne(1).boolVar();
    m.arithm(edgySays, "!=", edgy).post();

    // "That's right: it was Artie and Dodgy together." (Fingers)
    BoolVar fingersSays = artie.eq(1).and(dodgy.eq(1)).boolVar();
    m.arithm(fingersSays, "!=", fingers).post();

    out.put("artie", artie);
    out.put("bill", bill);
    out.put("crackitt", crackitt);
    out.put("dodgy", dodgy);
    out.put("edgy", edgy);
    out.put("fingers", fingers);
  }
}
