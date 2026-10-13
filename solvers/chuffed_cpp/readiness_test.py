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
# No branch() call and a free auxiliary variable: the driver's fallback search
# has to fix every variable, or Chuffed would report unfixed outputs.
UNBRANCHED = (HEAD + DECLARE + "  int_linear(terms, IRT_EQ, n);\n"
              "  IntVar* free_aux = newIntVar(0, 5);\n  (void)free_aux;\n" + EXPORT + TAIL)
UNCOMPILABLE = "this is not C++\n"

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
        check("optimum_enumeration", OPTIMAL.replace("DIRECTION", "OPT_MIN"), reference=OPTIMIZING, solution_limit=2)
        check("isolation", ISOLATED)
        check("malformed_output", MALFORMED, expected={"execution_error", "invalid_output"})
        check("empty_output", UNSATISFIABLE, expected={"no_solution"})
        check("timeout_cleanup", SLOW, expected={"execution_timeout"}, execution_timeout=2)
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
