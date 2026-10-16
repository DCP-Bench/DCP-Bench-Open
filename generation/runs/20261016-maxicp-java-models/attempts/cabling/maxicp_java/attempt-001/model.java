import java.util.HashMap;
import java.util.Map;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Cabling: place the devices in the rack, one device per 1U position, so that the
// sum of all cable lengths is as short as possible. A cable's length is the number
// of positions between its two devices; a device with several cables counts each.
// Print the optimal sum of all cable lengths (final_sum).
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    String[] devices = inst.getStringArray("devices");
    int n = devices.length;

    Map<String, Integer> index = new HashMap<>();
    for (int i = 0; i < n; i++) {
      index.put(devices[i], i);
    }

    // pos[d] is the rack position of device d, positions 0 to n-1
    CPIntVar[] pos = m.intVarArray(n, 0, n - 1);

    // every position holds exactly one device
    m.cp().post(allDifferent(pos));

    // each cable between two devices adds its length, the distance between their
    // positions, once for every cable of that pair
    JsonArray cables = inst.raw("cable_struct").getAsJsonArray();
    CPIntVar[] costs = new CPIntVar[cables.size()];
    int c = 0;
    for (JsonElement el : cables) {
      JsonArray row = el.getAsJsonArray();
      CPIntVar a = pos[index.get(row.get(0).getAsString())];
      CPIntVar b = pos[index.get(row.get(1).getAsString())];
      int count = row.get(2).getAsInt();

      // length of the cable: the distance between the two positions, at least
      // the difference in either direction; the minimum is the exact distance
      CPIntVar length = m.intVar(0, n - 1);
      m.cp().post(ge(length, sum(a, minus(b))));
      m.cp().post(ge(length, sum(b, minus(a))));

      // a cable is counted once for each cable of this pair
      costs[c++] = mul(length, count);
    }

    // the sum of all cable lengths is minimised
    CPIntVar total = sum(costs);
    m.minimize(total);

    out.put("final_sum", total);
  }
}
