import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Contracting costs: a contractor pays six men for their services. Each payment to a pair
// of men is given, and the task is to find what each man charges.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // what each man charges for his services, in dollars
    IntVar paperHanger = m.intVar("paper_hanger", 0, 10000, true);
    IntVar painter = m.intVar("painter", 0, 10000, true);
    IntVar plumber = m.intVar("plumber", 0, 10000, true);
    IntVar electrician = m.intVar("electrician", 0, 10000, true);
    IntVar carpenter = m.intVar("carpenter", 0, 10000, true);
    IntVar mason = m.intVar("mason", 0, 10000, true);

    // $1,100 to the paper hanger and the painter
    m.sum(new IntVar[]{paperHanger, painter}, "=", 1100).post();
    // $1,700 to the painter and plumber
    m.sum(new IntVar[]{painter, plumber}, "=", 1700).post();
    // $1,100 to the plumber and electrician
    m.sum(new IntVar[]{plumber, electrician}, "=", 1100).post();
    // $3,300 to the electrician and carpenter
    m.sum(new IntVar[]{electrician, carpenter}, "=", 3300).post();
    // $5,300 to the carpenter and mason
    m.sum(new IntVar[]{carpenter, mason}, "=", 5300).post();
    // $3,200 to the mason and painter
    m.sum(new IntVar[]{mason, painter}, "=", 3200).post();

    out.put("paper_hanger", paperHanger);
    out.put("painter", painter);
    out.put("plumber", plumber);
    out.put("electrician", electrician);
    out.put("carpenter", carpenter);
    out.put("mason", mason);
  }
}
