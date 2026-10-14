"""Readiness checks for the gecode_cpp integration and its current image.

Drives the repository evaluator against real containers, prints a JSON object
mapping check name to Boolean on stdout, and exits nonzero if any check failed.
`python -m generation.readiness check --solver gecode_cpp` runs this and keeps
its output as the readiness evidence.

Every submission is one translation unit that declares a class derived from
dcp::Space and ends with DCP_MODEL. The image compiles it against the driver.
"""
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from evaluation import evaluate
from evaluation.execution import image_identity
from evaluation.results import EvaluationError

SOLVER = "gecode_cpp"

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
solution = {"x": int(x.value()), "y": int(y.value())}
print(json.dumps(solution))
'''
OPTIMIZING = REFERENCE.replace("optimize = False", "optimize = True")
MAXIMIZING = OPTIMIZING.replace("model.minimize", "model.maximize")
FLAG_REFERENCE = REFERENCE.replace(
    'solution = {"x": int(x.value()), "y": int(y.value())}',
    'solution = {"x": int(x.value()), "y": int(y.value()), "flag": bool(x.value() == 0)}')
CONSTANT_REFERENCE = REFERENCE.replace(
    'solution = {"x": int(x.value()), "y": int(y.value())}',
    'solution = {"x": int(x.value()), "y": int(y.value()), "k": 5}')
CLONE_REFERENCE = REFERENCE.replace(
    'solution = {"x": int(x.value()), "y": int(y.value())}',
    'solution = {"x": int(x.value()), "y": int(y.value()), '
    '"m": [[int(x.value()), int(y.value())], [int(y.value()), int(x.value())]]}')

# Shared model text. Every model declares x and y as outputs, so each one
# matches the reference's output names.
HEAD = '''#include "dcp.h"

class Model : public dcp::Space {
  IntVarArray v;
 public:
  explicit Model(const json& instance) : v(*this, 2, 0, instance.at("n").get<int>()) {
    int n = instance.at("n");
'''
SUM = '''    IntVarArgs xy(2);
    xy[0] = v[0];
    xy[1] = v[1];
'''
BRANCH = "    branch(*this, v, INT_VAR_SIZE_MIN(), INT_VAL_MIN());\n"
OUTPUTS = '''    output("x", v[0]);
    output("y", v[1]);
'''
CLOSE = '''  }
  Model(Model& s) : dcp::Space(s) { v.update(*this, s.v); }
  Gecode::Space* copy() override { return new Model(*this); }
};
DCP_MODEL(Model)
'''


def optimal(direction):
    # Minimize or maximize x+y with x+y >= n. The objective is an auxiliary
    # variable, so the fallback branching has to fix it.
    return (HEAD + SUM + "    linear(*this, xy, IRT_GQ, n);\n"
            "    IntVar total(*this, 0, 2 * n);\n"
            "    IntVarArgs all(3);\n"
            "    all[0] = v[0];\n    all[1] = v[1];\n    all[2] = total;\n"
            "    linear(*this, IntArgs({1, 1, -1}), all, IRT_EQ, 0);\n"
            f"    {direction}(total);\n" + BRANCH + OUTPUTS + CLOSE)


GOOD = HEAD + SUM + "    linear(*this, xy, IRT_EQ, n);\n" + BRANCH + OUTPUTS + CLOSE
OPTIMAL_MIN = optimal("minimize")
# The first solution (x=2, y=1, total 3) is one above the optimum 2, so a bound
# that is off by one ends the search at 3.
STEP_ONE = optimal("minimize").replace(
    BRANCH, "    branch(*this, v[0], INT_VAL_MAX());\n    branch(*this, v[1], INT_VAL_MED());\n")
OPTIMAL_MAX = optimal("maximize")
# Restarts with activity-based branching. Optimality must still be proven.
RESTARTS = (HEAD + SUM + "    linear(*this, xy, IRT_GQ, n);\n"
            "    IntVar total(*this, 0, 2 * n);\n"
            "    IntVarArgs all(3);\n"
            "    all[0] = v[0];\n    all[1] = v[1];\n    all[2] = total;\n"
            "    linear(*this, IntArgs({1, 1, -1}), all, IRT_EQ, 0);\n"
            "    restarts(100);\n"
            "    minimize(total);\n"
            "    branch(*this, v, INT_VAR_AFC_SIZE_MAX(0.99), INT_VAL_MIN());\n"
            + OUTPUTS + CLOSE)
# A constrained auxiliary that the model never branches on. It is fixed by
# propagation, so the solution is correct; it must not be accepted wrong.
UNBRANCHED = (HEAD + SUM + "    linear(*this, xy, IRT_EQ, n);\n"
              "    IntVar aux(*this, 0, 5);\n"
              "    IntVarArgs ax(2);\n    ax[0] = v[0];\n    ax[1] = aux;\n"
              "    linear(*this, IntArgs({1, -1}), ax, IRT_EQ, 0);\n"
              + BRANCH + OUTPUTS + CLOSE)
UNBRANCHED_FREE = (HEAD + SUM + "    linear(*this, xy, IRT_EQ, n);\n"
                   "    IntVar free_aux(*this, 0, 5);\n  (void)free_aux;\n"
                   + BRANCH + OUTPUTS + CLOSE)
UNSATISFIABLE = (HEAD + "    rel(*this, v[0], IRT_EQ, 0);\n    rel(*this, v[0], IRT_EQ, 1);\n"
                 + BRANCH + OUTPUTS + CLOSE)
# Compiles and solves, but registers no outputs: the driver must reject it.
MALFORMED = HEAD + SUM + "    linear(*this, xy, IRT_EQ, n);\n" + BRANCH + CLOSE
# Pigeonhole with value propagation only: 20 pigeons, 19 holes. Resolution
# style search needs exponentially many steps, so the search outlasts any budget.
SLOW = (HEAD + SUM + "    linear(*this, xy, IRT_EQ, n);\n"
        "    IntVarArray pigeons(*this, 20, 0, 18);\n"
        "    distinct(*this, pigeons, IPL_VAL);\n"
        "    branch(*this, pigeons, INT_VAR_SIZE_MIN(), INT_VAL_MIN());\n"
        + BRANCH + OUTPUTS + CLOSE)
# Solutions come fast but the optimum needs the pigeonhole proof. The driver
# must report a timeout and emit nothing unproven.
OPTIMUM_UNPROVEN = (HEAD + SUM + "    linear(*this, xy, IRT_EQ, n);\n"
                    "    IntVarArray pigeons(*this, 20, 0, 19);\n"
                    "    distinct(*this, pigeons, IPL_VAL);\n"
                    "    IntVar top(*this, 0, 19);\n"
                    "    for (int i = 0; i < 20; ++i) rel(*this, pigeons[i], IRT_LQ, top);\n"
                    "    minimize(top);\n"
                    "    branch(*this, pigeons, INT_VAR_SIZE_MIN(), INT_VAL_MIN());\n"
                    + BRANCH + OUTPUTS + CLOSE)
UNCOMPILABLE = "this is not C++\n"
# Several arrays and a matrix output, so cloning must copy every registration.
CLONING = (HEAD + SUM + "    linear(*this, xy, IRT_EQ, n);\n"
           "    IntVarArray cells(*this, 4, 0, n);\n"
           "    rel(*this, cells[0], IRT_EQ, v[0]);\n    rel(*this, cells[1], IRT_EQ, v[1]);\n"
           "    rel(*this, cells[2], IRT_EQ, v[1]);\n    rel(*this, cells[3], IRT_EQ, v[0]);\n"
           "    Matrix<IntVarArray> m(cells, 2, 2);\n    output(\"m\", m);\n"
           + BRANCH + OUTPUTS + CLOSE)
# A Boolean output, reified from an integer comparison.
BOOL_OUTPUT = (HEAD + SUM + "    linear(*this, xy, IRT_EQ, n);\n"
               "    BoolVar flag(*this, 0, 1);\n"
               "    rel(*this, v[0], IRT_EQ, 0, flag);\n    output(\"flag\", flag);\n"
               + BRANCH + OUTPUTS + CLOSE)
# A constant output: the value is fixed in the output layout.
CONSTANT_OUTPUT = (HEAD + SUM + "    linear(*this, xy, IRT_EQ, n);\n"
                   "    output(\"k\", 5);\n"
                   + BRANCH + OUTPUTS + CLOSE)
# Probes run in the model constructor. A failed probe throws, and the driver
# reports an execution error, so the check passes only when every probe held.
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

static void Probe() {
  if (getuid() == 0) throw std::runtime_error("container runs as root");
  if (std::filesystem::exists("/dataset")) throw std::runtime_error("dataset is visible to the candidate");
  std::set<std::string> entries;
  for (const auto& entry : std::filesystem::directory_iterator("/input"))
    entries.insert(entry.path().filename().string());
  if (entries != std::set<std::string>{"model.cpp", "request.json"}) throw std::runtime_error("unexpected /input");
  std::ofstream written("/input/written");
  if (written.is_open()) throw std::runtime_error("input is writable");
  if (Reachable()) throw std::runtime_error("network reachable");
}

class Model : public dcp::Space {
  IntVarArray v;
 public:
  explicit Model(const json& instance) : v(*this, 2, 0, instance.at("n").get<int>()) {
    Probe();
    int n = instance.at("n");
    IntVarArgs xy(2);
    xy[0] = v[0];
    xy[1] = v[1];
    linear(*this, xy, IRT_EQ, n);
    branch(*this, v, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    output("x", v[0]);
    output("y", v[1]);
  }
  Model(Model& s) : dcp::Space(s) { v.update(*this, s.v); }
  Gecode::Space* copy() override { return new Model(*this); }
};
DCP_MODEL(Model)
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
        check("minimization", OPTIMAL_MIN, reference=OPTIMIZING)
        check("maximization", OPTIMAL_MAX, reference=MAXIMIZING)
        check("unbranched_fixed", UNBRANCHED_FREE, solution_limit=3)
        check("unbranched_aux", UNBRANCHED, solution_limit=3)
        check("optimum_enumeration", OPTIMAL_MIN, reference=OPTIMIZING, solution_limit=2)
        check("optimum_one_below_first", STEP_ONE, reference=OPTIMIZING, solution_limit=1)
        check("restarts", RESTARTS, reference=OPTIMIZING, solution_limit=3)
        check("bool_output", BOOL_OUTPUT, reference=FLAG_REFERENCE, solution_limit=2)
        check("constant_output", CONSTANT_OUTPUT, reference=CONSTANT_REFERENCE)
        check("cloning", CLONING, reference=CLONE_REFERENCE, solution_limit=3)
        check("isolation", ISOLATED)
        check("malformed_output", MALFORMED, expected={"execution_error", "invalid_output"})
        check("empty_output", UNSATISFIABLE, expected={"no_solution"})
        check("timeout_cleanup", SLOW, expected={"execution_timeout"}, execution_timeout=2)
        check("optimum_unproven_timeout", OPTIMUM_UNPROVEN, expected={"execution_timeout"}, execution_timeout=3)
        check("compilation_error", UNCOMPILABLE, expected={"compilation_error"})

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
