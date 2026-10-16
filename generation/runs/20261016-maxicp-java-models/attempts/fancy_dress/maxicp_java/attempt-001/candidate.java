import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Fancy dress party: the male guests must wear green dresses. Mr Greenguest owns
// a green shirt (so the shirt costs nothing) and can buy a green tie ($10), a green
// hat ($2) and green socks ($12). A guest who breaks rules 1-3 pays a $11 entrance
// fee. Choose the outfit (t tie, h hat, r shirt, s socks) and the fee n (0/1) so that
// the total cost is minimised.
public class Submission {

  public static void build(Instance inst, Model m, Outputs out) {
    CPBoolVar t = m.boolVar(); // green tie
    CPBoolVar h = m.boolVar(); // green hat
    CPBoolVar r = m.boolVar(); // green shirt
    CPBoolVar s = m.boolVar(); // green socks
    CPBoolVar n = m.boolVar(); // pays the entrance fee

    // rule 1 is broken: if someone wears a green tie he has to wear a green shirt
    CPBoolVar v1 = m.boolVar();
    equivAnd(m, v1, t, not(r));

    // rule 2 is broken: a guest may only wear green socks and a green shirt if he
    // wears a green tie or a green hat
    CPBoolVar v2 = m.boolVar();
    equivAnd(m, v2, s, r, not(t), not(h));

    // rule 3 is broken: a guest wearing a green shirt or a green hat or who does not
    // wear green socks must wear a green tie
    CPBoolVar wearsOrNoSocks = m.boolVar();
    equivOr(m, wearsOrNoSocks, r, h, not(s));
    CPBoolVar v3 = m.boolVar();
    equivAnd(m, v3, wearsOrNoSocks, not(t));

    // a guest not dressed according to rules 1-3 must pay the $11 entrance fee
    equivOr(m, n, v1, v2, v3);

    // total cost: tie $10, hat $2, socks $12, entrance fee $11 (shirt owned)
    CPIntVar cost = m.intVar(0, 35);
    m.cp().post(eq(cost, sum(new CPIntVar[] {
        mul(t, 10), mul(h, 2), mul(s, 12), mul(n, 11) })));
    m.minimize(cost);

    out.put("t", t);
    out.put("h", h);
    out.put("r", r);
    out.put("s", s);
    out.put("n", n);
  }

  // c is true exactly when all literals ls are true
  private static void equivAnd(Model m, CPBoolVar c, CPBoolVar... ls) {
    for (CPBoolVar l : ls) {
      m.cp().post(or(new CPBoolVar[] { not(c), l }));
    }
    CPBoolVar[] clause = new CPBoolVar[ls.length + 1];
    clause[0] = c;
    for (int i = 0; i < ls.length; i++) clause[i + 1] = not(ls[i]);
    m.cp().post(or(clause));
  }

  // c is true exactly when at least one literal in ls is true
  private static void equivOr(Model m, CPBoolVar c, CPBoolVar... ls) {
    for (CPBoolVar l : ls) {
      m.cp().post(or(new CPBoolVar[] { not(l), c }));
    }
    CPBoolVar[] clause = new CPBoolVar[ls.length + 1];
    clause[0] = not(c);
    for (int i = 0; i < ls.length; i++) clause[i + 1] = ls[i];
    m.cp().post(or(clause));
  }
}
