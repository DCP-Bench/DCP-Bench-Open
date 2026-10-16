// Abbot's puzzle: 100 people (men, women, children) share 100 bushels of corn,
// each man gets 3 bushels, each woman 2, each child 1/2 bushel, and there are
// five times as many women as men. Find the number of men, women and children.
import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // the puzzle fixes 100 people and 100 bushels; the instance has no fields
    int people = 100;
    int bushels = 100;

    IntVar men = m.intVar("men", 0, people);
    IntVar women = m.intVar("women", 0, people);
    IntVar children = m.intVar("children", 0, people);

    // 100 people: men, women and children together make up everyone
    m.sum(new IntVar[]{men, women, children}, "=", people).post();

    // five times as many women as men
    m.scalar(new IntVar[]{women, men}, new int[]{1, -5}, "=", 0).post();

    // the corn: each man 3 bushels, each woman 2, each child 1/2 bushel.
    // Counted in half-bushels so every coefficient is an integer:
    // 6 per man, 4 per woman, 1 per child, 2 * 100 = 200 half-bushels in all
    m.scalar(new IntVar[]{men, women, children}, new int[]{6, 4, 1}, "=", 2 * bushels).post();

    out.put("men", men);
    out.put("women", women);
    out.put("children", children);
  }
}
