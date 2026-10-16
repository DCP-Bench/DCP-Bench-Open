import org.chocosolver.solver.Model;
import org.chocosolver.solver.search.strategy.Search;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Ages of the three sons of an old man, found by a sequence of statements: the product of
// the ages is 36, the sum is ambiguous, and the oldest son's unique age settles the question.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // the ages of the three sons, oldest first
    IntVar[] age = m.intVarArray("age", 3, 1, 36);

    // "The product of their ages is 36."
    age[0].mul(age[1]).mul(age[2]).eq(36).post();

    // the ages are listed from the oldest
    age[0].ge(age[1]).post();
    age[1].ge(age[2]).post();

    // "The sum of their ages equals the number of windows in that building."
    IntVar sum = m.intVar("sum", 3, 108);
    m.sum(age, "=", sum).post();

    // The candidate triples: all triples of positive whole numbers, oldest first, whose
    // product is 36 (the factorisations of 36, worked out by hand). Each row is {age1, age2, age3}.
    int[][] candidates = {
        {36, 1, 1}, {18, 2, 1}, {12, 3, 1}, {9, 4, 1},
        {9, 2, 2}, {6, 6, 1}, {6, 3, 2}, {4, 3, 3}
    };

    // "I need more information." (second time): the sum of the answer is shared with
    // at least one other candidate. same[j] is 1 when candidate j has the same sum.
    BoolVar[] same = new BoolVar[candidates.length];
    for (int j = 0; j < candidates.length; j++) {
      int s = candidates[j][0] + candidates[j][1] + candidates[j][2];
      same[j] = sum.eq(s).boolVar();
    }
    m.sum(same, ">=", 2).post();

    // "The oldest son has blue eyes." "I got it.": among the candidates with the same sum,
    // only one has a unique oldest son. A candidate with a tied oldest son (6, 6, 1) cannot
    // be the answer, so only candidates with a unique oldest son are checked.
    for (int[] c : candidates) {
      if (c[0] > c[1]) {
        int s = c[0] + c[1] + c[2];
        m.ifThen(
            m.arithm(sum, "=", s),
            m.and(
                m.arithm(age[0], "=", c[0]),
                m.arithm(age[1], "=", c[1]),
                m.arithm(age[2], "=", c[2])));
      }
    }

    // the answer's oldest son is unique, so the blue-eyed clue identifies him
    age[0].gt(age[1]).post();

    // the search branches on the ages; the sum follows from them
    m.getSolver().setSearch(Search.inputOrderLBSearch(age));

    out.put("A1", age[0]);
    out.put("A2", age[1]);
    out.put("A3", age[2]);
  }
}
