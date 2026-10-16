import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Session 3 Exodus: five children (Bernice, Carl, Debby, Sammy, Ted) each have an age (3, 5, 7, 8, 10),
// a family's country of origin (Ethiopia, Kazakhstan, Lithuania, Morocco, Yemen) and a part of the Exodus
// story (burning bush, captivity, Moses's youth, Passover, Ten Commandments). The four output arrays hold
// the numbers 1..5; the same number in two arrays means the same child.
public class Submission {

  // the ages in the order of the problem statement
  static final int[] AGES = {3, 5, 7, 8, 10};

  // reified booleans b[k][v] = (xs[k] == v+1), for v in 0..n-1
  static CPBoolVar[][] indicators(CPIntVar[] xs, int n) {
    CPBoolVar[][] b = new CPBoolVar[xs.length][n];
    for (int k = 0; k < xs.length; k++)
      for (int v = 0; v < n; v++)
        b[k][v] = isEq(xs[k], v + 1);
    return b;
  }

  public static void build(Instance inst, Model m, Outputs out) {
    int n = 5;

    // the four mappings from category items to the numbers 1..5
    CPIntVar[] ages = m.intVarArray(n, 1, n);
    CPIntVar[] children = m.intVarArray(n, 1, n);
    CPIntVar[] countries = m.intVarArray(n, 1, n);
    CPIntVar[] stories = m.intVarArray(n, 1, n);

    // each child, country and story belongs to exactly one number
    m.cp().post(allDifferent(ages));
    m.cp().post(allDifferent(children));
    m.cp().post(allDifferent(countries));
    m.cp().post(allDifferent(stories));

    // each child is a different age (three, five, seven, eight, or ten): the age of a child, country
    // or story is the age of the age item that carries the same number
    CPIntVar[] ageOfChild = m.intVarArray(n, 3, 10);
    CPIntVar[] ageOfCountry = m.intVarArray(n, 3, 10);
    CPIntVar[] ageOfStory = m.intVarArray(n, 3, 10);
    CPBoolVar[][] ageInd = indicators(ages, n);
    link(m, children, ageOfChild, ageInd, n);
    link(m, countries, ageOfCountry, ageInd, n);
    link(m, stories, ageOfStory, ageInd, n);

    // Debby's family is from Lithuania
    m.cp().post(eq(children[2], countries[2]));

    // the child who told the story of the Passover is two years older than Bernice
    m.cp().post(eq(ageOfStory[3], plus(ageOfChild[0], 2)));

    // the child whose family is from Yemen is younger than the child from the Ethiopian family
    m.cp().post(ge(ageOfCountry[0], plus(ageOfCountry[4], 1)));

    // the child from the Moroccan family is three years older than Ted
    m.cp().post(eq(ageOfCountry[3], plus(ageOfChild[4], 3)));

    // Sammy is three years older than the child who told the story of Moses's youth in the house of the Pharaoh
    m.cp().post(eq(ageOfChild[3], plus(ageOfStory[2], 3)));

    out.put("ages", ages);
    out.put("children", children);
    out.put("countries", countries);
    out.put("stories", stories);
  }

  // an item and an age that carry the same number have the same age
  static void link(Model m, CPIntVar[] xs, CPIntVar[] ageOf, CPBoolVar[][] ageInd, int n) {
    CPBoolVar[][] ind = indicators(xs, n);
    for (int k = 0; k < xs.length; k++)
      for (int v = 0; v < n; v++)
        for (int l = 0; l < n; l++)
          m.cp().post(or(new CPBoolVar[] {not(ind[k][v]), not(ageInd[l][v]), isEq(ageOf[k], AGES[l])}));
  }
}
