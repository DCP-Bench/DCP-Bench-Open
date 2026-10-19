"""Readiness checks for the chuffed_cpp integration and its current image.

Drives the repository evaluator against real containers, prints a JSON object
mapping check name to Boolean on stdout, and exits nonzero if any check failed.
`python -m generation.readiness check --solver chuffed_cpp` runs this and
keeps its output as the readiness evidence.

A submission is one translation unit defining `Build`, which the image compiles
against the integration's driver, so this integration also has to prove that a
submission which does not compile is reported as `compilation_error` rather than
as some downstream failure. Every check below pays a real compile, which is why
this script is the slowest of the six.
"""
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from evaluation import evaluate
from evaluation.execution import image_identity
from evaluation.results import EvaluationError

SOLVER = "chuffed_cpp"

# A tiny trusted reference, kept here so this script does not depend on the
# test suite. n=2 gives x+y==2 exactly three solutions.
REFERENCE = '''
# Data
n = 2
optimize = False
# End of data
import cpmpy as cp
import json
x = cp.intvar(0, n, name="x")
y = cp.intvar(0, n, name="y")
model = cp.Model(x + y >= n if optimize else x + y == n)
if optimize:
    model.minimize(x + y)
model.solve()
solution = {"x": int(x.value()), "y": y.value()}
print(json.dumps(solution))
'''
OPTIMIZING = REFERENCE.replace("optimize = False", "optimize = True")
MAXIMIZING = OPTIMIZING.replace("model.minimize", "model.maximize")

# Trusted references (CPMpy), copied verbatim from solvers/cpmpy_python/readiness_test.py.
EASY_MIN = """
# Data
n = 2
# End of data
import cpmpy as cp
import json
x = cp.intvar(0, 10, name="x")
model = cp.Model(x >= n)
model.minimize(x)
model.solve()
solution = {"x": int(x.value())}
print(json.dumps(solution))
"""
STEP_REF = EASY_MIN.replace("x >= n", "x >= n - 1")
SUM_REF = """
# Data
n = 2
# End of data
import cpmpy as cp
import json
x = cp.intvar(0, 2, shape=4, name="x")
model = cp.Model(cp.sum(x) >= n)
model.minimize(cp.sum(x))
model.solve()
solution = {"x": x.value().tolist()}
print(json.dumps(solution))
"""
SHAPES_REF = """
# Data
n = 2
# End of data
import cpmpy as cp
import json
cube = cp.intvar(0, 10, shape=(2, 2, 2), name="cube")
grid = cp.boolvar(shape=(2, 2), name="grid")
big = cp.intvar(0, 40000000000, name="big")
model = cp.Model([cube[i, j, k] == i + j + k + n for i in range(2) for j in range(2) for k in range(2)],
                 [grid[i, j] == (i == j) for i in range(2) for j in range(2)],
                 big == 30000000000 + n)
model.solve()
solution = {"cube": cube.value().tolist(), "grid": grid.value().tolist(), "big": int(big.value())}
print(json.dumps(solution))
"""
SHAPED_REF = """
# Data
n = 2
rows = [[1], [2, 3]]
mixed = [[1, "a"], [2, "b"]]
label = "first"
# End of data
import cpmpy as cp
import json
total = cp.intvar(0, 1000, name="total")
key = cp.intvar(0, 1000, name="key")
model = cp.Model(total == n + sum(sum(row) for row in rows), key == sum(row[0] for row in mixed))
model.solve()
solution = {"total": int(total.value()), "key": int(key.value())}
print(json.dumps(solution))
"""
SHAPED_INSTANCE = {"n": 3, "rows": [[4, 5, 6], [], [1]], "mixed": [[3, "c"]], "label": "second",
                   "name": "readiness", "note": "ragged rows, mixed rows, an unused string"}
LARGE_REF = """
# Data
n = 1500
# End of data
import cpmpy as cp
import json
b = cp.boolvar(shape=3000, name="b")
count = cp.intvar(0, 3000, name="count")
model = cp.Model(count == cp.sum(b), count == n)
model.solve()
solution = {"b": b.value().tolist(), "count": int(count.value())}
print(json.dumps(solution))
"""

HEAD = '''#include "dcp.h"

void Build(const json& instance, json& outputs) {
'''
TAIL = "}\n"
DECLARE = ("  int n = instance.at(\"n\");\n"
           "  IntVar* x = newIntVar(0, n);\n"
           "  IntVar* y = newIntVar(0, n);\n"
           "  vec<IntVar*> terms; terms.push(x); terms.push(y);\n")
EXPORT = "  outputs = {{\"x\", dcp::out(x)}, {\"y\", dcp::out(y)}};\n"

GOOD = HEAD + DECLARE + "  int_linear(terms, IRT_EQ, n);\n" + EXPORT + TAIL
OPTIMAL = (HEAD + DECLARE + "  IntVar* total = newIntVar(0, 2 * n);\n"
           "  int_linear(terms, IRT_EQ, total);\n"
           "  int_rel(total, IRT_GE, n);\n"
           "  optimize(total, DIRECTION);\n" + EXPORT + TAIL)
# Compiles and solves; the driver rejects the empty output dictionary.
MALFORMED = HEAD + DECLARE + "  int_linear(terms, IRT_EQ, n);\n  outputs = json::object();\n" + TAIL
UNSATISFIABLE = (HEAD + DECLARE + "  int_rel(x, IRT_EQ, 0);\n  int_rel(x, IRT_EQ, 1);\n"
                 + EXPORT + TAIL)
# Pigeonhole with plain disequalities: 20 pigeons, 19 holes. Resolution-based
# learning needs exponentially many steps, so the search outlasts any budget.
SLOW = (HEAD + DECLARE + "  int_linear(terms, IRT_EQ, n);\n"
        "  vec<IntVar*> pigeons;\n"
        "  for (int i = 0; i < 20; ++i) pigeons.push(newIntVar(0, 18));\n"
        "  for (int i = 0; i < 20; ++i)\n"
        "    for (int j = i + 1; j < 20; ++j) int_rel(pigeons[i], IRT_NE, pigeons[j]);\n"
        + EXPORT + TAIL)
# Solutions come fast but the optimum needs the pigeonhole proof (20 pigeons
# need hole 19). The driver must report a timeout and emit nothing unproven,
# even when it kills the solving process at the deadline.
OPTIMUM_UNPROVEN = (HEAD + DECLARE + "  int_linear(terms, IRT_EQ, n);\n"
                    "  vec<IntVar*> pigeons;\n"
                    "  for (int i = 0; i < 20; ++i) pigeons.push(newIntVar(0, 19));\n"
                    "  for (int i = 0; i < 20; ++i)\n"
                    "    for (int j = i + 1; j < 20; ++j) int_rel(pigeons[i], IRT_NE, pigeons[j]);\n"
                    "  IntVar* top = newIntVar(0, 19);\n"
                    "  for (int i = 0; i < 20; ++i) int_rel(pigeons[i], IRT_LE, top);\n"
                    "  optimize(top, OPT_MIN);\n"
                    "  branch(pigeons, VAR_INORDER, VAL_MAX);\n"
                    + EXPORT + TAIL)
# No branch() call and a free auxiliary variable: the driver's fallback search
# has to fix every variable, or Chuffed would report unfixed outputs.
UNBRANCHED = (HEAD + DECLARE + "  int_linear(terms, IRT_EQ, n);\n"
              "  IntVar* free_aux = newIntVar(0, 5);\n  (void)free_aux;\n" + EXPORT + TAIL)
UNCOMPILABLE = "this is not C++\n"

# ---------------------------------------------------------------------------
# Bug-class checks (readiness level 2). The reference constants above are CPMpy and
# are shared with the other integrations; each submission below is C++ written in
# this integration's form (Build, dcp::out, optimize, branch) and mirrors the cpmpy
# submission of the same name in solvers/cpmpy_python/readiness_test.py.

# optimization_timeout: the objective adds an 11-mark Golomb ruler (optimum 72) to x.
# Solutions come at once, but the proof cannot finish in the 3 s budget, so the driver
# must report a timeout and emit nothing.
UNPROVABLE = (HEAD + "  int n = instance.at(\"n\");\n"
              "  IntVar* x = newIntVar(0, 10);\n"
              "  int_rel(x, IRT_GE, n);\n"
              "  vec<IntVar*> marks;\n"
              "  for (int i = 0; i < 11; ++i) marks.push(newIntVar(0, 200));\n"
              "  int_rel(marks[0], IRT_EQ, 0);\n"
              "  for (int i = 0; i < 10; ++i) int_rel(marks[i], IRT_LT, marks[i + 1]);\n"
              "  vec<IntVar*> diffs;\n"
              "  for (int i = 0; i < 11; ++i) {\n"
              "    for (int j = i + 1; j < 11; ++j) {\n"
              "      IntVar* d = newIntVar(1, 200);\n"
              "      vec<int> sign; sign.push(1); sign.push(-1);\n"
              "      vec<IntVar*> pair; pair.push(marks[j]); pair.push(marks[i]);\n"
              "      int_linear(sign, pair, IRT_EQ, d);\n"
              "      diffs.push(d);\n"
              "    }\n"
              "  }\n"
              "  all_different(diffs);\n"
              "  IntVar* obj = newIntVar(0, 10200);\n"
              "  vec<int> coeffs; coeffs.push(1000); coeffs.push(1);\n"
              "  vec<IntVar*> terms2; terms2.push(x); terms2.push(marks[10]);\n"
              "  int_linear(coeffs, terms2, IRT_EQ, obj);\n"
              "  branch(marks, VAR_INORDER, VAL_MIN);\n"
              "  optimize(obj, OPT_MIN);\n"
              "  outputs = {{\"x\", dcp::out(x)}};\n" + TAIL)
# minimization_step_one: x is confined to {n-1, n} and the search takes the largest value
# first, so the first solution is x = n = optimum + 1; the runner must then prove x = n-1.
# The objective is a separate IntVar built from x: optimising the branched variable itself
# lets Chuffed start from the optimum (traced in scratch by instrumenting the driver callback).
STEP = (HEAD + "  int n = instance.at(\"n\");\n"
        "  IntVar* x = newIntVar(0, 10);\n"
        "  int_rel(x, IRT_GE, n - 1);\n"
        "  int_rel(x, IRT_LE, n);\n"
        "  vec<IntVar*> decide; decide.push(x);\n"
        "  branch(decide, VAR_INORDER, VAL_MAX);\n"
        "  IntVar* obj = newIntVar(0, 10);\n"
        "  vec<int> one; one.push(1);\n"
        "  vec<IntVar*> copy; copy.push(x);\n"
        "  int_linear(one, copy, IRT_EQ, obj);\n"
        "  optimize(obj, OPT_MIN);\n"
        "  outputs = {{\"x\", dcp::out(x)}};\n" + TAIL)
# optimum_enumeration: four values in 0..2 with a sum of at least n and a sum objective:
# ten optima, of which three are enumerated.
SUM = (HEAD + "  int n = instance.at(\"n\");\n"
       "  vec<IntVar*> x;\n"
       "  for (int i = 0; i < 4; ++i) x.push(newIntVar(0, 2));\n"
       "  int_linear(x, IRT_GE, n);\n"
       "  IntVar* total = newIntVar(0, 8);\n"
       "  int_linear(x, IRT_EQ, total);\n"
       "  optimize(total, OPT_MIN);\n"
       "  json cells = json::array();\n"
       "  for (int i = 0; i < 4; ++i) cells.push_back(dcp::out(x[i]));\n"
       "  outputs = {{\"x\", cells}};\n" + TAIL)
# output_shapes: a 2x2x2 integer cube and a 2x2 Boolean grid (0/1 IntVars) are carried; the
# 30000000000 scalar is beyond Chuffed's 32-bit values and no shape can split it, so Build
# refuses it. CONTRACT.md ## Outputs documents this limit.
SHAPES = (HEAD + "  int n = instance.at(\"n\");\n"
          "  json cube = json::array();\n"
          "  for (int i = 0; i < 2; ++i) {\n"
          "    json plane = json::array();\n"
          "    for (int j = 0; j < 2; ++j) {\n"
          "      json row = json::array();\n"
          "      for (int k = 0; k < 2; ++k) {\n"
          "        IntVar* c = newIntVar(0, 10);\n"
          "        int_rel(c, IRT_EQ, i + j + k + n);\n"
          "        row.push_back(dcp::out(c));\n"
          "      }\n"
          "      plane.push_back(row);\n"
          "    }\n"
          "    cube.push_back(plane);\n"
          "  }\n"
          "  json grid = json::array();\n"
          "  for (int i = 0; i < 2; ++i) {\n"
          "    json row = json::array();\n"
          "    for (int j = 0; j < 2; ++j) {\n"
          "      IntVar* g = newIntVar(0, 1);\n"
          "      int_rel(g, IRT_EQ, i == j ? 1 : 0);\n"
          "      row.push_back(dcp::out(g));\n"
          "    }\n"
          "    grid.push_back(row);\n"
          "  }\n"
          "  outputs = {{\"cube\", cube}, {\"grid\", grid}};\n"
          "  throw std::runtime_error(\"output 'big' needs 30000000002, beyond the 32-bit range of Chuffed values\");\n"
          + TAIL)
# instance_shapes: ragged rows, mixed rows, an unused string field; the sums are read from the
# instance, so the submission follows whatever data it is given.
SHAPED = (HEAD + "  int n = instance.at(\"n\");\n"
          "  int total_value = n;\n"
          "  for (const auto& row : instance.at(\"rows\"))\n"
          "    for (const auto& item : row) total_value += item.get<int>();\n"
          "  int key_value = 0;\n"
          "  for (const auto& row : instance.at(\"mixed\")) key_value += row[0].get<int>();\n"
          "  outputs = {{\"total\", dcp::out(getConstant(total_value))},"
          " {\"key\", dcp::out(getConstant(key_value))}};\n" + TAIL)
# error_detail: the instance lacks the field the model reads; the JSON library's own
# out_of_range message must come back as the detail of an execution_error.
FAILING = (HEAD + "  int bound = instance.at(\"bound\");\n"
           "  IntVar* x = newIntVar(0, bound);\n"
           "  outputs = {{\"x\", dcp::out(x)}};\n" + TAIL)
# stray_stdout: the model prints while it is built; the protocol stream must survive it.
CHATTY = ('#include "dcp.h"\n#include <cstdio>\n#include <iostream>\n\nvoid Build(const json& instance, json& outputs) {\n'
          "  std::cout << \"building the model\\n\";\n"
          "  std::printf(\"building for n\\n\");\n"
          + DECLARE + "  int_linear(terms, IRT_EQ, n);\n" + EXPORT + TAIL)
# auxiliary_free_distinct: a free auxiliary variable outside the outputs must not repeat solutions.
AUXILIARY = (HEAD + DECLARE + "  int_linear(terms, IRT_EQ, n);\n"
             "  IntVar* spare = newIntVar(0, 5);\n"
             "  int_rel(spare, IRT_GE, 0);\n" + EXPORT + TAIL)
# large_model: 3000 0/1 decisions in one sum, reported as outputs.
LARGE = (HEAD + "  int n = instance.at(\"n\");\n"
         "  vec<IntVar*> bits;\n"
         "  for (int i = 0; i < 3000; ++i) bits.push(newIntVar(0, 1));\n"
         "  IntVar* count = newIntVar(0, 3000);\n"
         "  int_linear(bits, IRT_EQ, count);\n"
         "  int_rel(count, IRT_EQ, n);\n"
         "  json cells = json::array();\n"
         "  for (int i = 0; i < 3000; ++i) cells.push_back(dcp::out(bits[i]));\n"
         "  outputs = {{\"b\", cells}, {\"count\", dcp::out(count)}};\n" + TAIL)

# C++ can inspect its own container, so unlike MiniZinc and ASP this check runs
# through the real submission path. A failed probe throws, which the driver
# reports as an execution error, so the check only passes when every probe held.
ISOLATED = '''#include <cerrno>
#include <fcntl.h>
#include <filesystem>
#include <fstream>
#include <poll.h>
#include <set>
#include <string>
#include <unistd.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include "dcp.h"

static bool Reachable() {
  int fd = socket(AF_INET, SOCK_STREAM, 0);
  if (fd < 0) return false;
  fcntl(fd, F_SETFL, O_NONBLOCK);
  sockaddr_in address{};
  address.sin_family = AF_INET;
  address.sin_port = htons(443);
  inet_pton(AF_INET, "1.1.1.1", &address.sin_addr);
  if (connect(fd, reinterpret_cast<sockaddr*>(&address), sizeof(address)) == 0) {
    close(fd);
    return true;
  }
  if (errno != EINPROGRESS) {
    close(fd);
    return false;
  }
  pollfd waiting{fd, POLLOUT, 0};
  int error = 0;
  socklen_t length = sizeof(error);
  bool ready = poll(&waiting, 1, 500) > 0;
  if (ready) getsockopt(fd, SOL_SOCKET, SO_ERROR, &error, &length);
  close(fd);
  return ready && error == 0;
}

void Build(const json& instance, json& outputs) {
  if (getuid() == 0) throw std::runtime_error("container runs as root");
  if (std::filesystem::exists("/dataset")) throw std::runtime_error("dataset is visible to the candidate");
  std::set<std::string> entries;
  for (const auto& entry : std::filesystem::directory_iterator("/input"))
    entries.insert(entry.path().filename().string());
  if (entries != std::set<std::string>{"model.cpp", "request.json"}) throw std::runtime_error("unexpected /input");
  std::ofstream written("/input/written");
  if (written.is_open()) throw std::runtime_error("input is writable");
  if (Reachable()) throw std::runtime_error("network reachable");
  int n = instance.at("n");
  IntVar* x = newIntVar(0, n);
  IntVar* y = newIntVar(0, n);
  vec<IntVar*> terms; terms.push(x); terms.push(y);
  int_linear(terms, IRT_EQ, n);
  outputs = {{"x", dcp::out(x)}, {"y", dcp::out(y)}};
}
'''


def main():
    results = {}
    with tempfile.TemporaryDirectory(prefix="dcp_readiness_") as directory:
        temp = Path(directory)

        def candidate(name, source):
            path = temp / f"{name}.cpp"
            path.write_text(source, encoding="utf-8")
            return path

        def check(name, source, reference=REFERENCE, expected=None, **kwargs):
            result = evaluate(candidate(name, source), "readiness", SOLVER,
                              reference_source=reference, **kwargs)
            results[name] = result["accepted"] if expected is None else (
                not result["accepted"] and result["reason"] in expected)
            return result

        check("satisfaction", GOOD)
        check("changed_instances", GOOD, instances=[{"n": 3, "optimize": False}], instance_count=2)
        check("enumeration", GOOD, solution_limit=3)
        check("minimization", OPTIMAL.replace("DIRECTION", "OPT_MIN"), reference=OPTIMIZING)
        check("maximization", OPTIMAL.replace("DIRECTION", "OPT_MAX"), reference=MAXIMIZING)
        check("unbranched_fixed", UNBRANCHED, solution_limit=3)
        check("optimum_pair_enumeration", OPTIMAL.replace("DIRECTION", "OPT_MIN"), reference=OPTIMIZING,
              solution_limit=2)
        check("isolation", ISOLATED)
        check("malformed_output", MALFORMED, expected={"execution_error", "invalid_output"})
        check("empty_output", UNSATISFIABLE, expected={"no_solution"})
        check("timeout_cleanup", SLOW, expected={"execution_timeout"}, execution_timeout=2)
        check("optimum_unproven_timeout", OPTIMUM_UNPROVEN, expected={"execution_timeout"}, execution_timeout=3)
        check("compilation_error", UNCOMPILABLE, expected={"compilation_error"})

        # Bug-class checks (readiness level 2).
        result = evaluate(candidate("optimization_timeout", UNPROVABLE), "readiness", SOLVER,
                          reference_source=EASY_MIN, execution_timeout=3)
        results["optimization_timeout"] = (result["reason"] == "execution_timeout"
                                           and all(item.get("solutions_received", 0) == 0
                                                   for item in result["instances"]))
        check("minimization_step_one", STEP, reference=STEP_REF)
        result = check("optimum_enumeration", SUM, reference=SUM_REF, solution_limit=3)
        results["optimum_enumeration"] = result["accepted"] and result["solutions_checked"] == 3
        # The 32-bit refusal is the documented limit, raised by Build as an execution_error.
        result = evaluate(candidate("output_shapes", SHAPES), "readiness", SOLVER,
                          reference_source=SHAPES_REF)
        results["output_shapes"] = (result["reason"] == "execution_error"
                                    and "32-bit" in result.get("detail", ""))
        check("instance_shapes", SHAPED, reference=SHAPED_REF, instances=[SHAPED_INSTANCE], instance_count=2)
        result = evaluate(candidate("error_detail", FAILING), "readiness", SOLVER, reference_source=REFERENCE)
        results["error_detail"] = (result["reason"] == "execution_error"
                                   and "bound" in result.get("detail", "")
                                   and "not found" in result.get("detail", ""))
        check("stray_stdout", CHATTY)
        result = check("auxiliary_free_distinct", AUXILIARY, solution_limit=3)
        results["auxiliary_free_distinct"] = result["accepted"] and result["solutions_checked"] == 3
        check("large_model", LARGE, reference=LARGE_REF, execution_timeout=120, reference_timeout=120)

    try:
        image_identity({"id": SOLVER, "image": "dcp-eval/definitely-absent:readiness"})
        results["missing_image"] = False
    except EvaluationError as error:
        results["missing_image"] = error.reason == "infrastructure_error"

    print(json.dumps(results, sort_keys=True))
    if not all(results.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
