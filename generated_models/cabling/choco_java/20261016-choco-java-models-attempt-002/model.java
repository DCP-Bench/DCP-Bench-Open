// Cabling: place n devices in the slots of a rack, one device per slot, so that the
// sum of all cable lengths is as short as possible. A cable between two devices is as
// long as the number of slots between them, and some pairs are joined by several cables.
import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import dcp.Instance;
import dcp.Outputs;
import java.util.HashMap;
import java.util.Map;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");
    String[] devices = inst.getStringArray("devices");
    Map<String, Integer> index = new HashMap<>();
    for (int d = 0; d < devices.length; d++) index.put(devices[d], d);

    // slot of each device in the rack, 1 to n; one device per slot
    IntVar[] slot = m.intVarArray("slot", n, 1, n);
    m.allDifferent(slot, "AC").post();

    // cable_struct rows are [device, device, number of cables]; the shape is mixed, so read raw
    JsonArray cables = inst.raw("cable_struct").getAsJsonArray();
    IntVar[] lengths = new IntVar[cables.size()];
    int[] counts = new int[cables.size()];
    for (int c = 0; c < cables.size(); c++) {
      JsonArray row = cables.get(c).getAsJsonArray();
      int a = index.get(row.get(0).getAsString());
      int b = index.get(row.get(1).getAsString());
      counts[c] = row.get(2).getAsInt();
      // length of one cable between the two devices: the distance between their slots
      lengths[c] = slot[a].dist(slot[b]).intVar();
    }

    // total cable length: each cable of a pair counts its own length
    int maxLen = n - 1;
    int totalCables = 0;
    for (int c : counts) totalCables += c;
    IntVar total = m.intVar("total_cable_length", 0, totalCables * maxLen, true);
    m.scalar(lengths, counts, "=", total).post();
    m.setObjective(Model.MINIMIZE, total);

    out.put("final_sum", total);
  }
}
