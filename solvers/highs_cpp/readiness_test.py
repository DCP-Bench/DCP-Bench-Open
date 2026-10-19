"""Readiness checks for the highs_cpp integration and its current image.

Drives the repository evaluator against real containers, prints a JSON object
mapping check name to Boolean on stdout, and exits nonzero if any check failed.
`python -m generation.readiness check --solver highs_cpp` runs this and keeps
its output as the readiness evidence.

Every submission is one C++ file that includes dcp.h and defines
build(instance, Highs&, dcp::Outputs&). The image compiles it against the driver.
"""
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from evaluation import evaluate
from evaluation.execution import image_identity
from evaluation.results import EvaluationError

SOLVER = "highs_cpp"

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
NESTED_REFERENCE = REFERENCE.replace(
    'solution = {"x": int(x.value()), "y": int(y.value())}',
    'solution = {"x": int(x.value()), "y": int(y.value()), '
    '"cube": [[[int(x.value()), int(y.value())], [int(y.value()), int(x.value())]]], '
    '"flags": [[bool(x.value() == 0), bool(y.value() == 0)]], '
    '"big": 30000000000 + 10 * int(x.value()) + int(y.value())}')

# Shared model text. Every model declares x and y as outputs, so each one
# matches the reference's output names.
GOOD = '''#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int n = instance.at("n");
  dcp::Lin x = dcp::new_var(h, 0, n);
  dcp::Lin y = dcp::new_var(h, 0, n);
  dcp::add_row(h, x + y, n, n);
  out.add("x", x);
  out.add("y", y);
}
'''


def optimal(direction):
    # Minimise or maximise x+y with x+y >= n, over 0..n. The objective is
    # declared with out.minimize / out.maximize.
    return f'''#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {{
  int n = instance.at("n");
  dcp::Lin x = dcp::new_var(h, 0, n);
  dcp::Lin y = dcp::new_var(h, 0, n);
  dcp::add_row(h, x + y, n, kHighsInf);
  out.{direction}(x + y);
  out.add("x", x);
  out.add("y", y);
}}
'''


OPTIMAL_MIN = optimal("minimize")
OPTIMAL_MAX = optimal("maximize")
# The first solution the optimiser finds need not be the optimum; objective
# offsets and negative coefficients must not change the answer. The reference
# minimises 2x - 3y - 5 over -3..3 with x + y >= -2 (optimum x=-2... checked by CPMpy).
OFFSET_REF = """
# Data
n = 3
# End of data
import cpmpy as cp
import json
x = cp.intvar(-n, n, name="x")
y = cp.intvar(-n, n, name="y")
model = cp.Model(x + y >= -2)
model.minimize(2 * x - 3 * y - 5)
model.solve()
solution = {"x": int(x.value()), "y": int(y.value())}
print(json.dumps(solution))
"""
OFFSET_MIN = '''#include "dcp.h"

// Minimise 2x - 3y - 5 with x + y >= -2 over -3..3: a negative offset and negative terms.
void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int n = instance.at("n");
  dcp::Lin x = dcp::new_var(h, -n, n);
  dcp::Lin y = dcp::new_var(h, -n, n);
  dcp::add_row(h, x + y, -2, kHighsInf);
  out.minimize(2 * x - 3 * y - 5);
  out.add("x", x);
  out.add("y", y);
}
'''
# The maximise counterpart: maximise -x + 2y + 7 with x + y >= -2 over -3..3.
OFFSET_MAX_REF = OFFSET_REF.replace("model.minimize(2 * x - 3 * y - 5)",
                                    "model.maximize(-x + 2 * y + 7)")
OFFSET_MAX = OFFSET_MIN.replace("minimize(2 * x - 3 * y - 5)", "maximize(-x + 2 * y + 7)").replace(
    "Minimise 2x - 3y - 5", "Maximise -x + 2y + 7").replace("a negative offset and negative terms",
                                                             "a positive offset and negative terms")
# Integer outputs within tolerance: columns fixed at -2.999999 and -1e-7 must be
# reported as -3 and 0. The reference states the integers.
ROUNDING_REF = """
# Data
n = 1
# End of data
import cpmpy as cp
import json
v = cp.intvar(-5, 5, name="v")
w = cp.intvar(-5, 5, name="w")
model = cp.Model(v == -3, w == 0)
model.solve()
solution = {"v": int(v.value()), "w": int(w.value()), "neg": int(-v.value())}
print(json.dumps(solution))
"""
ROUNDING = '''#include "dcp.h"

// Two columns fixed just off integers (within the 1e-5 tolerance); the outputs
// must come back as -3 and 0, and -v as 3.
void build(const json& instance, Highs& h, dcp::Outputs& out) {
  dcp::Lin v = dcp::new_var(h, -2.999999, -2.999999, false);
  dcp::Lin w = dcp::new_var(h, -1e-7, -1e-7, false);
  out.add("v", v);
  out.add("w", w);
  out.add("neg", -1.0 * v);
}
'''
# A flag and a constant output, a free Boolean-as-0/1 column.
BOOL_OUTPUT = '''#include "dcp.h"

// flag is 1 exactly when x == 0, for x in 0..n: x + n*flag <= n and x + flag >= 1.
dcp::Lin zero_flag(Highs& h, const dcp::Lin& x, int n) {
  dcp::Lin f = dcp::new_var(h, 0, 1);
  dcp::add_row(h, x + n * f, -kHighsInf, n);
  dcp::add_row(h, x + f, 1, kHighsInf);
  return f;
}

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int n = instance.at("n");
  dcp::Lin x = dcp::new_var(h, 0, n);
  dcp::Lin y = dcp::new_var(h, 0, n);
  dcp::add_row(h, x + y, n, n);
  out.add("x", x);
  out.add("y", y);
  out.add("flag", zero_flag(h, x, n));  // a Boolean output as 0/1
}
'''
CONSTANT_OUTPUT = '''#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int n = instance.at("n");
  dcp::Lin x = dcp::new_var(h, 0, n);
  dcp::Lin y = dcp::new_var(h, 0, n);
  dcp::add_row(h, x + y, n, n);
  out.add("x", x);
  out.add("y", y);
  out.add("k", 5);
}
'''
# Outputs three levels deep, a Boolean matrix, and a number above the 32-bit range.
NESTED = '''#include "dcp.h"

// flag is 1 exactly when x == 0, for x in 0..n: x + n*flag <= n and x + flag >= 1.
dcp::Lin zero_flag(Highs& h, const dcp::Lin& x, int n) {
  dcp::Lin f = dcp::new_var(h, 0, 1);
  dcp::add_row(h, x + n * f, -kHighsInf, n);
  dcp::add_row(h, x + f, 1, kHighsInf);
  return f;
}

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int n = instance.at("n");
  dcp::Lin x = dcp::new_var(h, 0, n);
  dcp::Lin y = dcp::new_var(h, 0, n);
  dcp::add_row(h, x + y, n, n);
  dcp::Lin f0 = zero_flag(h, x, n);
  dcp::Lin f1 = zero_flag(h, y, n);
  std::vector<std::vector<std::vector<dcp::Lin>>> cube = {{{x, y}, {y, x}}};
  std::vector<std::vector<dcp::Lin>> flags = {{f0, f1}};
  out.add("x", x);
  out.add("y", y);
  out.add("cube", cube);
  out.add("flags", flags);
  out.add("big", 30000000000.0 + 10 * x + y);
}
'''
# instance_shapes: the model reads ragged rows, rows of mixed types and name/note
# keys from the instance; string fields it does not use must be ignored.
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
SHAPED = '''#include "dcp.h"

// Reads the ragged and mixed fields from the JSON instance; label, name and note
// are ignored.
void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int total_value = instance.at("n").get<int>();
  for (const auto& row : instance.at("rows"))
    for (const auto& item : row) total_value += item.get<int>();
  int key_value = 0;
  for (const auto& row : instance.at("mixed")) key_value += row.at(0).get<int>();
  dcp::Lin total = dcp::new_var(h, total_value, total_value);
  dcp::Lin key = dcp::new_var(h, key_value, key_value);
  out.add("total", total);
  out.add("key", key);
}
'''
# error_detail: build throws; the driver must report an error with that message.
FAILING = '''#include <stdexcept>
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int n = instance.at("n");
  dcp::Lin x = dcp::new_var(h, 0, n);
  if (n >= 0) throw std::runtime_error("readiness: no value fits the domain of x");
  out.add("x", x);
}
'''
# stray_stdout: the model prints; the protocol stream must survive it.
CHATTY = '''#include <cstdio>
#include <iostream>
#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  std::cout << "building the model" << std::endl;
  printf("this line goes to stdout too\\n");
  int n = instance.at("n");
  dcp::Lin x = dcp::new_var(h, 0, n);
  dcp::Lin y = dcp::new_var(h, 0, n);
  dcp::add_row(h, x + y, n, n);
  out.add("x", x);
  out.add("y", y);
}
'''
# auxiliary_free_distinct: a free auxiliary column outside the outputs must not
# repeat output solutions.
AUXILIARY = '''#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int n = instance.at("n");
  dcp::Lin x = dcp::new_var(h, 0, n);
  dcp::Lin y = dcp::new_var(h, 0, n);
  dcp::add_row(h, x + y, n, n);
  dcp::new_var(h, 0, 5);  // spare, not an output
  out.add("x", x);
  out.add("y", y);
}
'''
# optimum_enumeration: a compound objective (a sum) with ten optimal solutions.
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
SUM = '''#include "dcp.h"

// Four values in 0..2 with a sum of at least n, minimising the sum: the optimum
// has ten solutions.
void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int n = instance.at("n");
  std::vector<dcp::Lin> x;
  dcp::Lin total;
  for (int i = 0; i < 4; ++i) {
    x.push_back(dcp::new_var(h, 0, 2));
    total = total + x.back();
  }
  dcp::add_row(h, total, n, kHighsInf);
  out.minimize(total);
  out.add("x", x);
}
'''
# output_shapes: a three-level integer array, a Boolean matrix and a value beyond 32 bits.
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
SHAPES = '''#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int n = instance.at("n");
  std::vector<std::vector<std::vector<dcp::Lin>>> cube(
      2, std::vector<std::vector<dcp::Lin>>(2, std::vector<dcp::Lin>(2)));
  for (int i = 0; i < 2; ++i)
    for (int j = 0; j < 2; ++j)
      for (int k = 0; k < 2; ++k) {
        cube[i][j][k] = dcp::new_var(h, 0, 10);
        dcp::add_row(h, cube[i][j][k], i + j + k + n, i + j + k + n);
      }
  std::vector<std::vector<dcp::Lin>> grid(2, std::vector<dcp::Lin>(2));
  for (int i = 0; i < 2; ++i)
    for (int j = 0; j < 2; ++j) {
      grid[i][j] = dcp::new_var(h, 0, 1);
      dcp::add_row(h, grid[i][j], i == j ? 1 : 0, i == j ? 1 : 0);
    }
  dcp::Lin big = dcp::new_var(h, 30000000000.0 + n, 30000000000.0 + n);
  out.add("cube", cube);
  out.add("grid", grid);
  out.add("big", big);
}
'''
# instance_shapes is checked with SHAPED_INSTANCE above.
# large_model: 3000 binaries in one sum, reported as an output.
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
LARGE = '''#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int n = instance.at("n");
  std::vector<dcp::Lin> b;
  dcp::Lin total;
  for (int i = 0; i < 3000; ++i) {
    b.push_back(dcp::new_var(h, 0, 1));
    total = total + b.back();
  }
  dcp::add_row(h, total, n, n);
  out.add("b", b);
  out.add("count", total);
}
'''
# optimization_timeout: the reference is easy (minimise x, optimum n); the submission
# adds an unrelated Golomb ruler to its objective, so the proof cannot finish within
# the budget. A correct runner emits nothing.
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
UNPROVABLE = '''#include "dcp.h"

// Minimise 1000 * x + (length of an eleven-mark Golomb ruler). The ruler is
// unrelated to x, so solutions come quickly but the proof does not.
void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int n = instance.at("n");
  dcp::Lin x = dcp::new_var(h, n, 10);
  const int marks_count = 11, length = 200;
  std::vector<dcp::Lin> marks;
  for (int i = 0; i < marks_count; ++i) marks.push_back(dcp::new_var(h, 0, length));
  dcp::add_row(h, marks[0], 0, 0);
  for (int i = 0; i + 1 < marks_count; ++i) dcp::add_row(h, marks[i + 1] - marks[i], 1, kHighsInf);
  // All differences distinct: for two pairs, diff = d_p - d_q lies in [1, M-1] when
  // s = 0 and in [1 - M, -1] when s = 1, with M = 401 (marks lie in 0..200).
  std::vector<std::pair<int, int>> pairs;
  for (int i = 0; i < marks_count; ++i)
    for (int j = i + 1; j < marks_count; ++j) pairs.push_back({i, j});
  const double M = 401;
  for (std::size_t p = 0; p < pairs.size(); ++p)
    for (std::size_t q = p + 1; q < pairs.size(); ++q) {
      dcp::Lin diff = (marks[pairs[p].second] - marks[pairs[p].first]) -
                      (marks[pairs[q].second] - marks[pairs[q].first]);
      dcp::Lin s = dcp::new_var(h, 0, 1);
      dcp::add_row(h, diff + M * s, 1, M - 1);
    }
  dcp::Lin total = 1000 * x + marks[marks_count - 1];
  out.minimize(total);
  out.add("x", x);
}
'''
# minimization_step_one: the optimum is n - 1 and the first solution is n. A bound that
# is off by one on the objective would stop at n.
STEP_REF = EASY_MIN.replace("x >= n", "x >= n - 1")
STEP = '''#include "dcp.h"

// Minimise x with x >= n - 1 over 0..n: the optimum is n - 1.
void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int n = instance.at("n");
  dcp::Lin x = dcp::new_var(h, 0, n);
  dcp::add_row(h, x, n - 1, kHighsInf);
  out.minimize(x);
  out.add("x", x);
}
'''
# timeout_cleanup: an eleven-mark Golomb ruler of length at most 71. The optimum is 72,
# so the system is infeasible, and HiGHS cannot prove it within the budget.
SLOW = '''#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int n = instance.at("n");
  const int marks_count = 11, length = 71;
  std::vector<dcp::Lin> marks;
  for (int i = 0; i < marks_count; ++i) marks.push_back(dcp::new_var(h, 0, length));
  dcp::add_row(h, marks[0], 0, 0);
  for (int i = 0; i + 1 < marks_count; ++i) dcp::add_row(h, marks[i + 1] - marks[i], 1, kHighsInf);
  std::vector<std::pair<int, int>> pairs;
  for (int i = 0; i < marks_count; ++i)
    for (int j = i + 1; j < marks_count; ++j) pairs.push_back({i, j});
  const double M = 401;
  for (std::size_t p = 0; p < pairs.size(); ++p)
    for (std::size_t q = p + 1; q < pairs.size(); ++q) {
      dcp::Lin diff = (marks[pairs[p].second] - marks[pairs[p].first]) -
                      (marks[pairs[q].second] - marks[pairs[q].first]);
      dcp::Lin s = dcp::new_var(h, 0, 1);
      dcp::add_row(h, diff + M * s, 1, M - 1);
    }
  dcp::Lin y = dcp::new_var(h, 0, n);
  dcp::add_row(h, y, n, n);
  out.add("y", y);
}
'''


UNCOMPILABLE = "this is not C++\n"
# Compiles and solves, but registers no outputs: the driver must reject it.
MALFORMED = '''#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  int n = instance.at("n");
  dcp::Lin x = dcp::new_var(h, 0, n);
  dcp::add_row(h, x, 0, n);
}
'''
# An infeasible constraint: the reference has solutions, so the answer is no_solution.
UNSATISFIABLE = '''#include "dcp.h"

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  dcp::Lin x = dcp::new_var(h, 0, 5);
  dcp::add_row(h, x, 0, 0);
  dcp::add_row(h, x, 1, 1);
  out.add("x", x);
}
'''
# isolation: the model probes the container from inside build; any failed probe throws.
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

void build(const json& instance, Highs& h, dcp::Outputs& out) {
  Probe();
  int n = instance.at("n");
  dcp::Lin x = dcp::new_var(h, 0, n);
  dcp::Lin y = dcp::new_var(h, 0, n);
  dcp::add_row(h, x + y, n, n);
  out.add("x", x);
  out.add("y", y);
}
'''
# Enumeration of a small satisfaction problem: exactly three solutions, no duplicates.
ENUMERATION = GOOD


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
        result = check("enumeration", ENUMERATION, solution_limit=10)
        results["enumeration"] = result["accepted"] and result["solutions_checked"] == 3
        check("minimization", OPTIMAL_MIN, reference=OPTIMIZING)
        check("maximization", OPTIMAL_MAX, reference=MAXIMIZING)
        check("optimum_enumeration", SUM, reference=SUM_REF, solution_limit=3)
        check("minimization_step_one", STEP, reference=STEP_REF, solution_limit=1)
        check("bool_output", BOOL_OUTPUT, reference=FLAG_REFERENCE, solution_limit=2)
        check("constant_output", CONSTANT_OUTPUT, reference=CONSTANT_REFERENCE)
        check("nested_outputs", NESTED, reference=NESTED_REFERENCE, solution_limit=3)
        check("isolation", ISOLATED)
        check("malformed_output", MALFORMED, expected={"execution_error", "invalid_output"})
        check("empty_output", UNSATISFIABLE, expected={"no_solution"})
        check("timeout_cleanup", SLOW, expected={"execution_timeout"}, execution_timeout=3)
        check("compilation_error", UNCOMPILABLE, expected={"compilation_error"})

        # Bug-class checks (readiness level 2).
        result = evaluate(candidate("optimization_timeout", UNPROVABLE), "readiness", SOLVER,
                          reference_source=EASY_MIN, execution_timeout=3)
        results["optimization_timeout"] = (result["reason"] == "execution_timeout"
                                           and all(item.get("solutions_received", 0) == 0
                                                   for item in result["instances"]))
        check("output_shapes", SHAPES, reference=SHAPES_REF)
        check("instance_shapes", SHAPED, reference=SHAPED_REF, instances=[SHAPED_INSTANCE], instance_count=2)
        result = evaluate(candidate("error_detail", FAILING), "readiness", SOLVER, reference_source=REFERENCE)
        results["error_detail"] = (result["reason"] == "execution_error"
                                   and "no value fits the domain" in json.dumps(result))
        check("stray_stdout", CHATTY)
        result = check("auxiliary_free_distinct", AUXILIARY, solution_limit=10)
        results["auxiliary_free_distinct"] = result["accepted"] and result["solutions_checked"] == 3
        check("large_model", LARGE, reference=LARGE_REF, execution_timeout=120, reference_timeout=120)
        # Objective offsets and negative coefficients, both directions.
        check("objective_offset_minimise", OFFSET_MIN, reference=OFFSET_REF)
        check("objective_offset_maximise", OFFSET_MAX, reference=OFFSET_MAX_REF)
        # Integer outputs within the tolerance, negative values and -0.
        check("rounding_within_tolerance", ROUNDING, reference=ROUNDING_REF)
        # Every solution of a small satisfaction problem, exactly once.
        result = check("enumeration_exact_count", ENUMERATION, solution_limit=10)
        # Accepted with a limit of 10 and 3 solutions: the search was exhausted, and no
        # output repeats (the evaluator counts distinct outputs).
        results["enumeration_exact_count"] = result["accepted"] and result["solutions_checked"] == 3
        # All optima of a compound objective, no suboptimal solution.
        result = check("optimal_enumeration_only_optima", SUM, reference=SUM_REF, solution_limit=20)
        results["optimal_enumeration_only_optima"] = result["accepted"] and result["solutions_checked"] == 10

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
