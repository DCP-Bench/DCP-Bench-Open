import org.chocosolver.solver.Model;
import org.chocosolver.solver.constraints.Constraint;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Fancy dress: Mr Greenguest chooses which green items to wear (tie, hat, socks) and
// whether his owned green shirt is worn, so that the party rules are met, or he pays
// the entrance fee. The cheapest way to participate is the objective.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // 0/1 choices: tie t, hat h, shirt r, socks s, and the entrance fee n
    BoolVar t = m.boolVar("t");
    BoolVar h = m.boolVar("h");
    BoolVar r = m.boolVar("r");
    BoolVar s = m.boolVar("s");
    BoolVar n = m.boolVar("n");

    // rule 1: if someone wears a green tie he has to wear a green shirt: t <= r
    Constraint rule1 = m.arithm(t, "<=", r);
    // rule 2: a guest may only wear green socks and a green shirt if he wears a
    // green tie or a green hat: s + r - t - h <= 1
    Constraint rule2 = m.scalar(new BoolVar[]{s, r, t, h}, new int[]{1, 1, -1, -1}, "<=", 1);
    // rule 3: a guest wearing a green shirt or a green hat or not wearing green socks
    // must wear a green tie: the tie is worn, or the shirt and hat are not green and the socks are
    Constraint rule3 = m.or(m.arithm(t, "=", 1),
        m.and(m.arithm(r, "=", 0), m.arithm(h, "=", 0), m.arithm(s, "=", 1)));

    // rule 4: a guest not dressed according to rules 1-3 pays the 11 entrance fee,
    // so the fee is due exactly when one of the rules is broken
    m.ifOnlyIf(m.and(rule1, rule2, rule3), m.arithm(n, "=", 0));

    // he owns a green shirt and wears it, so the shirt is worn green at no cost
    m.arithm(r, "=", 1).post();

    // cost: tie 10, hat 2, socks 12, fee 11
    IntVar cost = m.intVar("cost", 0, 35, true);
    m.scalar(new IntVar[]{t, h, s, n, cost}, new int[]{10, 2, 12, 11, -1}, "=", 0).post();

    // minimise the total cost
    m.setObjective(Model.MINIMIZE, cost);

    out.put("t", t);
    out.put("h", h);
    out.put("r", r);
    out.put("s", s);
    out.put("n", n);
  }
}
