#pragma once
// Header for Chuffed submissions. Start the submission with #include "dcp.h",
// then define Build. Output leaves are the indices returned by dcp::out.
#include <nlohmann/json.hpp>

#include "chuffed/branching/branching.h"
#include "chuffed/core/engine.h"
#include "chuffed/core/options.h"
#include "chuffed/core/propagator.h"
#include "chuffed/globals/globals.h"
#include "chuffed/primitives/primitives.h"
#include "chuffed/support/vec.h"
#include "chuffed/vars/bool-view.h"
#include "chuffed/vars/int-var.h"
#include "chuffed/vars/modelling.h"

using nlohmann::json;

namespace dcp {
// Registers an integer variable as an output and returns its index.
int out(IntVar* v);
}  // namespace dcp

// The submission defines this. Post the model on the Chuffed globals (engine, so)
// and describe the outputs as an object whose leaves are dcp::out indices.
// To optimize call optimize(var, OPT_MIN) or optimize(var, OPT_MAX).
void Build(const json& instance, json& outputs);
