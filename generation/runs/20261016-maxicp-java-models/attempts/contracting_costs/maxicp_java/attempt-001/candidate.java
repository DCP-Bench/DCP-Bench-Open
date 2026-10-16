import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Contracting costs: a contractor pays the men in pairs. What does each man
// charge for his services (paper hanger, painter, plumber, electrician,
// carpenter, mason), in dollars?
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    CPIntVar paperHanger = m.intVar(-10000, 10000);
    CPIntVar painter = m.intVar(-10000, 10000);
    CPIntVar plumber = m.intVar(-10000, 10000);
    CPIntVar electrician = m.intVar(-10000, 10000);
    CPIntVar carpenter = m.intVar(-10000, 10000);
    CPIntVar mason = m.intVar(-10000, 10000);

    // $1,100 to the paper hanger and the painter
    m.cp().post(eq(sum(new CPIntVar[] { paperHanger, painter }), 1100));
    // $1,700 to the painter and plumber
    m.cp().post(eq(sum(new CPIntVar[] { painter, plumber }), 1700));
    // $1,100 to the plumber and electrician
    m.cp().post(eq(sum(new CPIntVar[] { plumber, electrician }), 1100));
    // $3,300 to the electrician and carpenter
    m.cp().post(eq(sum(new CPIntVar[] { electrician, carpenter }), 3300));
    // $5,300 to the carpenter and mason
    m.cp().post(eq(sum(new CPIntVar[] { carpenter, mason }), 5300));
    // $3,200 to the mason and painter
    m.cp().post(eq(sum(new CPIntVar[] { mason, painter }), 3200));

    out.put("paper_hanger", paperHanger);
    out.put("painter", painter);
    out.put("plumber", plumber);
    out.put("electrician", electrician);
    out.put("carpenter", carpenter);
    out.put("mason", mason);
  }
}
