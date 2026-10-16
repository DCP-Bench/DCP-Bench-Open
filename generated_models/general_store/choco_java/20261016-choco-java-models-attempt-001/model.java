import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Cryptarithm: each letter stands for a different digit, and the sixteen addends
// CHESS, CASH, BOWWOW, CHOPS, ALSOPS, PALEALE, COOL, BASS, HOPS, ALES, HOES, APPLES,
// COWS, CHEESE, CHSOAP, SHEEP add up to ALL WOOL. Find the digits.
public class Submission {

  // the ten letters, in the order of the outputs
  static final String[] LETTERS = {"A", "B", "C", "E", "H", "L", "O", "P", "S", "W"};

  // place-value coefficients of a word over the letter variables
  static int[] coefficients(String word) {
    int[] coef = new int[LETTERS.length];
    int place = 1;
    for (int p = word.length() - 1; p >= 0; p--) {
      int idx = java.util.Arrays.asList(LETTERS).indexOf(String.valueOf(word.charAt(p)));
      coef[idx] += place;
      place *= 10;
    }
    return coef;
  }

  public static void build(Instance inst, Model m, Outputs out) {
    String[] addends = {"CHESS", "CASH", "BOWWOW", "CHOPS", "ALSOPS", "PALEALE", "COOL",
        "BASS", "HOPS", "ALES", "HOES", "APPLES", "COWS", "CHEESE", "CHSOAP", "SHEEP"};
    String total = "ALLWOOL";

    // each letter stands for a digit, and different letters stand for different digits
    IntVar[] L = new IntVar[LETTERS.length];
    for (int i = 0; i < LETTERS.length; i++) L[i] = m.intVar(LETTERS[i], 0, 9);
    m.allDifferent(L, "AC").post();

    // the value of each addend, as the letters in its place values
    IntVar[] values = new IntVar[addends.length];
    for (int j = 0; j < addends.length; j++) {
      // the addend is read as a base-10 number
      values[j] = m.intVar(addends[j], 0, 9999999, true);
      m.scalar(L, coefficients(addends[j]), "=", values[j]).post();
    }

    // the value of ALL WOOL, as the letters in its place values
    IntVar sum = m.intVar(total, 0, 9999999, true);
    m.scalar(L, coefficients(total), "=", sum).post();

    // the addends add up to ALL WOOL
    m.sum(values, "=", sum).post();

    for (int i = 0; i < LETTERS.length; i++) out.put(LETTERS[i], L[i]);
  }
}
