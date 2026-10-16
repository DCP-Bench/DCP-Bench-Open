// Handshaking problem: Hilary and Jocelyn are married and invite num_couples couples
// who are friends. Everyone shakes hands with each other, except nobody shakes hands
// with himself or herself or with his or her spouse. Jocelyn then asks how many hands
// each person has shaken, and all the answers are different. Output: hil, the number
// of hands Hilary has shaken.
//
// Encoding: persons 2c and 2c+1 are the spouses of couple c. Couple 0 is Hilary
// (person 0) and Jocelyn (person 1); couples 1..num_couples are the invited couples.
// Each unordered pair of persons gets one Boolean handshake variable, shared by both
// directions. Spouses have no variable, so they cannot shake hands.
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // num_couples invited couples, plus Hilary and Jocelyn's own couple
    int invited = inst.getInt("num_couples");
    int people = 2 * (invited + 1);
    // the largest answer: a person can shake hands with everyone but self and spouse
    int top = people - 2;

    // answer[p][v] = 1 if person p has shaken exactly v hands (one value per person)
    CPBoolVar[][] answer = new CPBoolVar[people][top + 1];
    for (int p = 0; p < people; p++) {
      if (p == 1) continue;   // Jocelyn gives no answer
      for (int v = 0; v <= top; v++) answer[p][v] = m.boolVar();
    }

    // one Boolean per unordered pair that are not spouses: handshake[i][j] = handshake[j][i]
    CPBoolVar[][] handshake = new CPBoolVar[people][people];
    for (int i = 0; i < people; i++) {
      for (int j = i + 1; j < people; j++) {
        // nobody shakes hands with his or her spouse
        if ((i ^ 1) == j) continue;
        handshake[i][j] = m.boolVar();
        handshake[j][i] = handshake[i][j];
      }
    }

    CPIntVar[] hands = new CPIntVar[people];
    for (int p = 0; p < people; p++) {
      // person p has shaken hands with the persons other than self and spouse
      CPIntVar[] shakes = new CPIntVar[people - 2];
      int k = 0;
      for (int q = 0; q < people; q++) {
        if (q == p || (p ^ 1) == q) continue;
        shakes[k++] = handshake[p][q];
      }
      hands[p] = m.intVar(0, top);
      m.cp().post(eq(hands[p], sum(shakes)));
      // the answer of each person who gives one is the number of hands counted above
      if (p == 1) continue;
      CPIntVar[] one = new CPIntVar[top + 1];
      for (int v = 0; v <= top; v++) one[v] = answer[p][v];
      m.cp().post(eq(sum(one), 1));
      for (int v = 0; v <= top; v++) m.cp().post(implies(answer[p][v], isEq(hands[p], v)));
    }

    // all the answers are different: everybody except Jocelyn (person 1), who asks
    // the question. She is not one of the answers. The answers fill 0..top, one each.
    for (int v = 0; v <= top; v++) {
      CPIntVar[] holders = new CPIntVar[people - 1];
      int a = 0;
      for (int p = 0; p < people; p++) {
        if (p == 1) continue;
        holders[a++] = answer[p][v];
      }
      m.cp().post(eq(sum(holders), 1));
    }

    // implied by the distinct answers (derived by peeling off the person who shook
    // everyone but a spouse and the person who shook nobody): the two spouses of each
    // invited couple have answers that add up to top.
    for (int c = 1; c <= invited; c++) {
      CPIntVar[] pair = {hands[2 * c], hands[2 * c + 1]};
      m.cp().post(eq(sum(pair), top));
      // so the answer v of one spouse goes with the answer top-v of the other
      for (int v = 0; v <= top; v++) {
        m.cp().post(eq(answer[2 * c][v], answer[2 * c + 1][top - v]));
      }
    }

    // the number of hands Hilary has shaken
    out.put("hil", hands[0]);
  }
}
