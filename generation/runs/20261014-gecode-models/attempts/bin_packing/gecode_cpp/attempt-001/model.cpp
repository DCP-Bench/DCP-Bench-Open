#include "dcp.h"

// Bin packing: assign each item to one of num_bins bins of a fixed capacity so
// that the total weight of the items in each bin does not exceed the capacity.
// Output: bins[i] is the 0-indexed bin of item i.
class BinPacking : public dcp::Space {
 protected:
  IntVarArray bin;   // bin[i]: bin of item i
  IntVarArray load;  // load[j]: total weight of the items in bin j

 public:
  explicit BinPacking(const json& instance) {
    std::vector<int> weights = instance.at("weights").get<std::vector<int>>();
    int capacity = instance.at("capacity").get<int>();
    int num_bins = instance.at("num_bins").get<int>();
    int n = static_cast<int>(weights.size());

    IntArgs size(n);
    for (int i = 0; i < n; ++i) size[i] = weights[i];

    bin = IntVarArray(*this, n, 0, num_bins - 1);
    // a bin holds at most the capacity: load[j] is bounded by the capacity
    load = IntVarArray(*this, num_bins, 0, capacity);

    // the weight of the items in each bin is its load
    binpacking(*this, load, bin, size);

    // the bins are identical, so bin j is first used only after bin j-1 (symmetry breaking)
    IntArgs bin_values(num_bins);
    for (int j = 0; j < num_bins; ++j) bin_values[j] = j;
    precede(*this, bin, bin_values);

    branch(*this, bin, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    output("bins", bin);
  }

  BinPacking(BinPacking& s) : dcp::Space(s) {
    bin.update(*this, s.bin);
    load.update(*this, s.load);
  }
  Gecode::Space* copy() override { return new BinPacking(*this); }
};

DCP_MODEL(BinPacking)
