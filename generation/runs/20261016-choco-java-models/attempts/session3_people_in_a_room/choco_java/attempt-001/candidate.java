import org.chocosolver.solver.Model;
import org.chocosolver.solver.search.strategy.Search;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
import java.util.Arrays;
import dcp.Instance;
import dcp.Outputs;

// People in a room: 13 people, 4 of them male, enter a room one at a time. Find an
// order of entry (0 = male, 1 = female) so that at any time the ratio of females to
// males in the room is no greater than 7/3.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // problem constants from the description: 13 people, 4 male, 9 female, ratio 7/3
    int people = 13, males = 4, females = people - males;
    int ratioNum = 7, ratioDen = 3;

    // female[i] = 1 if the i-th person to enter is female, 0 if male
    BoolVar[] female = m.boolVarArray("female", people);

    // exactly 9 females and 4 males enter in total
    m.sum(female, "=", females).post();

    // at every time k, F_k females and M_k = (k+1) - F_k males are in the room, and
    // the ratio F_k / M_k is at most 7/3, i.e. 3 * F_k <= 7 * M_k. Substituting M_k
    // gives 10 * F_k <= 7 * (k+1), which is the form posted here.
    IntVar[] inRoomFemales = new IntVar[people];
    for (int k = 0; k < people; k++) {
      int inRoom = k + 1;
      // F_k: number of females among the first inRoom entries
      inRoomFemales[k] = m.intVar("femalesIn_" + inRoom, 0, inRoom);
      m.sum(Arrays.copyOf(female, inRoom), "=", inRoomFemales[k]).post();
      // ratio of females to males in the room: 3 * F_k <= 7 * M_k
      // (with M_k = inRoom - F_k, so 10 * F_k <= 7 * inRoom)
      inRoomFemales[k].mul(ratioDen + ratioNum).le(ratioNum * inRoom).post();
    }

    // branch on entry order, male first
    m.getSolver().setSearch(Search.inputOrderLBSearch(female));

    out.put("sequence", female);
  }
}
