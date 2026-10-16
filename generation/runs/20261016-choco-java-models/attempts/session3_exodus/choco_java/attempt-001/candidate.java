import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Exodus puzzle: match each of five children to an age, a family origin country and
// the part of the Exodus story they told. Children are numbered 1..5 in the order
// Bernice, Carl, Debby, Sammy, Ted. Every list gives, for each entity of its category,
// the number of the child who has it.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // problem constants, from the statement
    int[] ageValues = {3, 5, 7, 8, 10};  // ages in the order listed in the statement
    int[] lithuania = {2};              // country index of Lithuania (order: Ethiopia, Kazakhstan, Lithuania, Morocco, Yemen)
    int ethiopia = 0, morocco = 3, yemen = 4;   // country indices
    int passover = 3, mosesYouth = 2;            // story indices (order: burning bush, captivity, Moses's youth, Passover, Ten Commandments)
    int bernice = 0, debby = 2, sammy = 3, ted = 4;  // child indices (order: Bernice, Carl, Debby, Sammy, Ted)

    // for each child: the index of their age, country and story
    IntVar[] ageSlot = m.intVarArray("ageSlot", 5, 0, 4);
    IntVar[] countrySlot = m.intVarArray("countrySlot", 5, 0, 4);
    IntVar[] storySlot = m.intVarArray("storySlot", 5, 0, 4);
    // for each slot: the child who has it
    IntVar[] ageHolder = m.intVarArray("ageHolder", 5, 0, 4);
    IntVar[] countryHolder = m.intVarArray("countryHolder", 5, 0, 4);
    IntVar[] storyHolder = m.intVarArray("storyHolder", 5, 0, 4);
    m.inverseChanneling(ageSlot, ageHolder).post();
    m.inverseChanneling(countrySlot, countryHolder).post();
    m.inverseChanneling(storySlot, storyHolder).post();

    // each child's real age, read from the list of ages
    IntVar[] age = new IntVar[5];
    for (int c = 0; c < 5; c++) {
      age[c] = m.intVar("age" + c, ageValues[0], ageValues[4], true);
      m.element(age[c], ageValues, ageSlot[c], 0).post();
    }

    // Debby's family is from Lithuania
    m.arithm(countrySlot[debby], "=", lithuania[0]).post();

    // the child who told the story of the Passover is two years older than Bernice
    IntVar passoverAge = m.intVar("passoverAge", ageValues[0], ageValues[4], true);
    m.element(passoverAge, age, storyHolder[passover], 0).post();
    m.arithm(passoverAge, "-", age[bernice], "=", 2).post();

    // the child whose family is from Yemen is younger than the child from the Ethiopian family
    IntVar yemenAge = m.intVar("yemenAge", ageValues[0], ageValues[4], true);
    IntVar ethiopiaAge = m.intVar("ethiopiaAge", ageValues[0], ageValues[4], true);
    m.element(yemenAge, age, countryHolder[yemen], 0).post();
    m.element(ethiopiaAge, age, countryHolder[ethiopia], 0).post();
    m.arithm(yemenAge, "<", ethiopiaAge).post();

    // the child from the Moroccan family is three years older than Ted
    IntVar moroccanAge = m.intVar("moroccanAge", ageValues[0], ageValues[4], true);
    m.element(moroccanAge, age, countryHolder[morocco], 0).post();
    m.arithm(moroccanAge, "-", age[ted], "=", 3).post();

    // Sammy is three years older than the child who told the story of Moses's youth in the house of the Pharaoh
    IntVar mosesAge = m.intVar("mosesAge", ageValues[0], ageValues[4], true);
    m.element(mosesAge, age, storyHolder[mosesYouth], 0).post();
    m.arithm(age[sammy], "-", mosesAge, "=", 3).post();

    // outputs: value = number of the child (1..5) who has that entity
    IntVar[] ages = new IntVar[5];
    IntVar[] countries = new IntVar[5];
    IntVar[] stories = new IntVar[5];
    IntVar[] children = new IntVar[5];
    for (int i = 0; i < 5; i++) {
      ages[i] = m.offset(ageHolder[i], 1);
      countries[i] = m.offset(countryHolder[i], 1);
      stories[i] = m.offset(storyHolder[i], 1);
      children[i] = m.intVar(i + 1);
    }
    out.put("ages", ages);
    out.put("children", children);
    out.put("countries", countries);
    out.put("stories", stories);
  }
}
