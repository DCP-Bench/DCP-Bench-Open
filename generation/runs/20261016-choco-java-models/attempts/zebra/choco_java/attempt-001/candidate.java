import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Zebra puzzle: five houses in a row, each with a colour, a nationality, a pet, a drink
// and a job, all different within each category, and the clues of the description hold.
// Each attribute value is a variable giving its house (0..4, left to right).
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // colours, in the order of the description: yellow, green, red, white, blue
    int YELLOW = 0, GREEN = 1, RED = 2, WHITE = 3, BLUE = 4;
    // nations: italy, spain, japan, england, norway
    int ITALY = 0, SPAIN = 1, JAPAN = 2, ENGLAND = 3, NORWAY = 4;
    // pets: cat, zebra, bear, snails, horse
    int CAT = 0, ZEBRA = 1, BEAR = 2, SNAILS = 3, HORSE = 4;
    // drinks: milk, water, tea, coffee, juice
    int MILK = 0, WATER = 1, TEA = 2, COFFEE = 3, JUICE = 4;
    // jobs: painter, sculptor, diplomat, pianist, doctor
    int PAINTER = 0, SCULPTOR = 1, DIPLOMAT = 2, PIANIST = 3, DOCTOR = 4;

    IntVar[] colors = m.intVarArray("colors", 5, 0, 4);
    IntVar[] nations = m.intVarArray("nations", 5, 0, 4);
    IntVar[] pets = m.intVarArray("pets", 5, 0, 4);
    IntVar[] drinks = m.intVarArray("drinks", 5, 0, 4);
    IntVar[] jobs = m.intVarArray("jobs", 5, 0, 4);

    // each house has a different colour, nationality, pet, drink and job
    m.allDifferent(colors, "AC").post();
    m.allDifferent(nations, "AC").post();
    m.allDifferent(pets, "AC").post();
    m.allDifferent(drinks, "AC").post();
    m.allDifferent(jobs, "AC").post();

    // the painter owns the horse
    m.arithm(jobs[PAINTER], "=", pets[HORSE]).post();
    // the diplomat drinks coffee
    m.arithm(jobs[DIPLOMAT], "=", drinks[COFFEE]).post();
    // the one who drinks milk lives in the white house
    m.arithm(drinks[MILK], "=", colors[WHITE]).post();
    // the Spaniard is a painter
    m.arithm(nations[SPAIN], "=", jobs[PAINTER]).post();
    // the Englishman lives in the red house
    m.arithm(nations[ENGLAND], "=", colors[RED]).post();
    // the snails are owned by the sculptor
    m.arithm(pets[SNAILS], "=", jobs[SCULPTOR]).post();
    // the green house is immediately on the left of the red one
    m.arithm(colors[RED], "-", colors[GREEN], "=", 1).post();
    // the Norwegian lives immediately on the right of the blue house
    m.arithm(nations[NORWAY], "-", colors[BLUE], "=", 1).post();
    // the doctor drinks milk
    m.arithm(jobs[DOCTOR], "=", drinks[MILK]).post();
    // the diplomat is Japanese
    m.arithm(jobs[DIPLOMAT], "=", nations[JAPAN]).post();
    // the Norwegian owns the zebra
    m.arithm(nations[NORWAY], "=", pets[ZEBRA]).post();
    // the green house is next to the white one
    colors[GREEN].dist(colors[WHITE]).eq(1).post();
    // the horse is owned by the neighbour of the diplomat
    pets[HORSE].dist(jobs[DIPLOMAT]).eq(1).post();
    // the Italian lives in the red, white or green house (five colours, so not blue)
    m.arithm(nations[ITALY], "!=", colors[BLUE]).post();

    out.put("colors", colors);
    out.put("drinks", drinks);
    out.put("jobs", jobs);
    out.put("nations", nations);
    out.put("pets", pets);
  }
}
