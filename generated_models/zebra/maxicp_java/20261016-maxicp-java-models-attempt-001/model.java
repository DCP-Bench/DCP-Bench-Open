import org.maxicp.cp.CPFactory;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Zebra puzzle: five houses in a row, numbered 0 to 4 from left to right.
// Each category (colors, nations, pets, drinks, jobs) assigns the five houses
// to its five values, so each category is a permutation of 0..4.
public class Submission {

  // Pairs of houses that are immediately next to each other, in either order.
  static int[][] neighbours() {
    return new int[][] {{0, 1}, {1, 0}, {1, 2}, {2, 1}, {2, 3}, {3, 2}, {3, 4}, {4, 3}};
  }

  public static void build(Instance inst, Model m, Outputs out) {
    // colors: yellow=0, green=1, red=2, white=3, blue=4
    CPIntVar[] colors = m.intVarArray(5, 0, 4);
    // nations: italy=0, spain=1, japan=2, england=3, norway=4
    CPIntVar[] nations = m.intVarArray(5, 0, 4);
    // pets: cat=0, zebra=1, bear=2, snails=3, horse=4
    CPIntVar[] pets = m.intVarArray(5, 0, 4);
    // drinks: milk=0, water=1, tea=2, coffee=3, juice=4
    CPIntVar[] drinks = m.intVarArray(5, 0, 4);
    // jobs: painter=0, sculptor=1, diplomat=2, pianist=3, doctor=4
    CPIntVar[] jobs = m.intVarArray(5, 0, 4);

    // The inhabitants are all of different nationalities, own different pets,
    // drink different beverages and have different jobs; each house is painted a different color.
    m.cp().post(allDifferent(colors));
    m.cp().post(allDifferent(nations));
    m.cp().post(allDifferent(pets));
    m.cp().post(allDifferent(drinks));
    m.cp().post(allDifferent(jobs));

    // the painter owns the horse
    m.cp().post(eq(jobs[0], pets[4]));
    // the diplomat drinks coffee
    m.cp().post(eq(jobs[2], drinks[3]));
    // the one who drinks milk lives in the white house
    m.cp().post(eq(drinks[0], colors[3]));
    // the Spaniard is a painter
    m.cp().post(eq(nations[1], jobs[0]));
    // the Englishman lives in the red house
    m.cp().post(eq(nations[3], colors[2]));
    // the snails are owned by the sculptor
    m.cp().post(eq(pets[3], jobs[1]));
    // the green house is immediately on the left of the red one
    m.cp().post(table(new CPIntVar[] {colors[1], colors[2]},
        new int[][] {{0, 1}, {1, 2}, {2, 3}, {3, 4}}));
    // the Norwegian lives immediately on the right of the blue house
    m.cp().post(table(new CPIntVar[] {nations[4], colors[4]},
        new int[][] {{1, 0}, {2, 1}, {3, 2}, {4, 3}}));
    // the doctor drinks milk
    m.cp().post(eq(jobs[4], drinks[0]));
    // the diplomat is Japanese
    m.cp().post(eq(jobs[2], nations[2]));
    // the Norwegian owns the zebra
    m.cp().post(eq(nations[4], pets[1]));
    // the green house is next to the white one
    m.cp().post(table(new CPIntVar[] {colors[1], colors[3]}, neighbours()));
    // the horse is owned by the neighbor of the diplomat
    m.cp().post(table(new CPIntVar[] {pets[4], jobs[2]}, neighbours()));
    // the Italian either lives in the red, white or green house
    // (so not in the yellow or the blue house)
    m.cp().post(neq(nations[0], colors[0]));
    m.cp().post(neq(nations[0], colors[4]));

    out.put("colors", colors);
    out.put("nations", nations);
    out.put("pets", pets);
    out.put("drinks", drinks);
    out.put("jobs", jobs);
  }
}
