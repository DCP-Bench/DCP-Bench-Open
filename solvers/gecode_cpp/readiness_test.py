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
NESTED_REFERENCE = REFERENCE.replace(
    'solution = {"x": int(x.value()), "y": int(y.value())}',
    'solution = {"x": int(x.value()), "y": int(y.value()), '
    '"cube": [[[int(x.value()), int(y.value())], [int(y.value()), int(x.value())]]], '
    '"flags": [[bool(x.value() == 0), bool(y.value() == 0)]], '
    '"big": 30000000000 + 10 * int(x.value()) + int(y.value())}')

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

# Outputs three levels deep, a Boolean matrix, and a number above the IntVar
# range given by its digits.
NESTED = (HEAD + SUM + "    linear(*this, xy, IRT_EQ, n);\n"
          "    BoolVarArray f(*this, 2, 0, 1);\n"
          "    rel(*this, v[0], IRT_EQ, 0, f[0]);\n"
          "    rel(*this, v[1], IRT_EQ, 0, f[1]);\n"
          "    IntVarArgs digits;\n"
          "    digits << IntVar(*this, 3, 3);\n"
          "    for (int i = 0; i < 8; ++i) digits << IntVar(*this, 0, 0);\n"
          "    digits << v[0] << v[1];\n"
          "    IntVarArgs r0, r1;\n"
          "    r0 << v[0] << v[1];\n    r1 << v[1] << v[0];\n"
          "    std::vector<std::vector<IntVarArgs>> cube(1);\n"
          "    cube[0].push_back(r0);\n    cube[0].push_back(r1);\n"
          "    output(\"cube\", cube);\n"
          "    output(\"flags\", Matrix<BoolVarArray>(f, 2, 1));\n"
          "    output_digits(\"big\", digits);\n"
          + BRANCH + OUTPUTS + CLOSE)

# ---------------------------------------------------------------------------
# Bug-class checks (readiness level 2). The trusted references are CPMpy programs,
# copied verbatim from solvers/cpmpy_python/readiness_test.py; each submission is
# this integration's own form of the same model.

# optimization_timeout: the reference is easy (minimise x, optimum n); the submission
# adds an unrelated Golomb ruler to its objective, so the search cannot prove the
# optimum within the budget. A correct runner emits nothing.
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
UNPROVABLE = ("#include \"dcp.h\"\n"
              "\n"
              "// Minimise 1000 * x + (length of an eleven-mark Golomb ruler). The ruler is\n"
              "// unrelated to x, so solutions come quickly but the proof does not.\n"
              "class Model : public dcp::Space {\n"
              " public:\n"
              "  explicit Model(const json& instance) {\n"
              "    int n = instance.at(\"n\");\n"
              "    IntVar x(*this, 0, 10);\n"
              "    IntVarArray marks(*this, 11, 0, 200);\n"
              "    rel(*this, x, IRT_GQ, n);\n"
              "    rel(*this, marks[0], IRT_EQ, 0);\n"
              "    for (int i = 0; i < 10; ++i) rel(*this, marks[i], IRT_LE, marks[i + 1]);\n"
              "    IntVarArgs diffs;\n"
              "    for (int i = 0; i < 11; ++i)\n"
              "      for (int j = i + 1; j < 11; ++j) diffs << expr(*this, marks[j] - marks[i]);\n"
              "    distinct(*this, diffs, IPL_DOM);\n"
              "    IntVar total = expr(*this, 1000 * x + marks[10]);\n"
              "    branch(*this, marks, INT_VAR_SIZE_MIN(), INT_VAL_MIN());\n"
              "    minimize(total);\n"
              "    output(\"x\", x);\n"
              "  }\n"
              "  Model(Model& s) : dcp::Space(s) {}\n"
              "  Gecode::Space* copy() override { return new Model(*this); }\n"
              "};\n"
              "DCP_MODEL(Model)\n")
# minimization_step_one: the optimum is 1 and the first solution is 2 = optimum + 1.
# The value order MAX on the domain 0..n reaches n first; a bound that is off by one
# on the objective would stop the search at 2.
STEP_REF = EASY_MIN.replace("x >= n", "x >= n - 1")
STEP = ("#include \"dcp.h\"\n"
        "\n"
        "// The first solution is the largest value of 0..n, optimum + 1 for x >= n - 1.\n"
        "class Model : public dcp::Space {\n"
        " public:\n"
        "  explicit Model(const json& instance) {\n"
        "    int n = instance.at(\"n\");\n"
        "    IntVar x(*this, 0, n);\n"
        "    rel(*this, x, IRT_GQ, n - 1);\n"
        "    branch(*this, x, INT_VAL_MAX());\n"
        "    minimize(x);\n"
        "    output(\"x\", x);\n"
        "  }\n"
        "  Model(Model& s) : dcp::Space(s) {}\n"
        "  Gecode::Space* copy() override { return new Model(*this); }\n"
        "};\n"
        "DCP_MODEL(Model)\n")
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
SUM = ("#include \"dcp.h\"\n"
       "\n"
       "// Four values in 0..2 with a sum of at least n, minimising the sum: the optimum\n"
       "// has ten solutions.\n"
       "class Model : public dcp::Space {\n"
       " public:\n"
       "  explicit Model(const json& instance) {\n"
       "    int n = instance.at(\"n\");\n"
       "    IntVarArray x(*this, 4, 0, 2);\n"
       "    IntVarArgs xs;\n"
       "    for (int i = 0; i < 4; ++i) xs << x[i];\n"
       "    linear(*this, xs, IRT_GQ, n);\n"
       "    IntVar total = expr(*this, sum(xs));\n"
       "    branch(*this, x, INT_VAR_SIZE_MIN(), INT_VAL_MIN());\n"
       "    minimize(total);\n"
       "    output(\"x\", x);\n"
       "  }\n"
       "  Model(Model& s) : dcp::Space(s) {}\n"
       "  Gecode::Space* copy() override { return new Model(*this); }\n"
       "};\n"
       "DCP_MODEL(Model)\n")
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
SHAPES = ("#include \"dcp.h\"\n"
          "\n"
          "class Model : public dcp::Space {\n"
          " public:\n"
          "  explicit Model(const json& instance) {\n"
          "    int n = instance.at(\"n\");\n"
          "    IntVarArray cube(*this, 8, 0, 10);\n"
          "    BoolVarArray grid(*this, 4, 0, 1);\n"
          "    std::vector<std::vector<IntVarArgs>> cells(2, std::vector<IntVarArgs>(2));\n"
          "    for (int i = 0; i < 2; ++i)\n"
          "      for (int j = 0; j < 2; ++j)\n"
          "        for (int k = 0; k < 2; ++k) {\n"
          "          int index = 4 * i + 2 * j + k;\n"
          "          rel(*this, cube[index], IRT_EQ, i + j + k + n);\n"
          "          cells[i][j] << cube[index];\n"
          "        }\n"
          "    std::vector<BoolVarArgs> rows(2);\n"
          "    for (int i = 0; i < 2; ++i)\n"
          "      for (int j = 0; j < 2; ++j) {\n"
          "        int index = 2 * i + j;\n"
          "        rel(*this, grid[index], IRT_EQ, i == j ? 1 : 0);\n"
          "        rows[i] << grid[index];\n"
          "      }\n"
          "    // 30000000000 + n as ten-base digits, most significant first; the digits are\n"
          "    // constants here, which is enough for the output to carry the wide value.\n"
          "    std::string text = std::to_string(30000000000LL + n);\n"
          "    IntVarArgs digits;\n"
          "    for (char c : text) digits << IntVar(*this, c - '0', c - '0');\n"
          "    output(\"cube\", cells);\n"
          "    output(\"grid\", rows);\n"
          "    output_digits(\"big\", digits);\n"
          "    branch(*this, cube, INT_VAR_SIZE_MIN(), INT_VAL_MIN());\n"
          "  }\n"
          "  Model(Model& s) : dcp::Space(s) {}\n"
          "  Gecode::Space* copy() override { return new Model(*this); }\n"
          "};\n"
          "DCP_MODEL(Model)\n")
# instance_shapes: ragged rows, rows of mixed types, a string field the model ignores,
# and name/note keys, on two instances with different shapes.
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
SHAPED = ("#include \"dcp.h\"\n"
          "\n"
          "// Reads the ragged and mixed fields from the JSON instance; label, name and note\n"
          "// are ignored.\n"
          "class Model : public dcp::Space {\n"
          " public:\n"
          "  explicit Model(const json& instance) {\n"
          "    int total_value = instance.at(\"n\").get<int>();\n"
          "    for (const auto& row : instance.at(\"rows\"))\n"
          "      for (const auto& item : row) total_value += item.get<int>();\n"
          "    int key_value = 0;\n"
          "    for (const auto& row : instance.at(\"mixed\")) key_value += row.at(0).get<int>();\n"
          "    IntVar total(*this, 0, 1000);\n"
          "    IntVar key(*this, 0, 1000);\n"
          "    rel(*this, total, IRT_EQ, total_value);\n"
          "    rel(*this, key, IRT_EQ, key_value);\n"
          "    output(\"total\", total);\n"
          "    output(\"key\", key);\n"
          "  }\n"
          "  Model(Model& s) : dcp::Space(s) {}\n"
          "  Gecode::Space* copy() override { return new Model(*this); }\n"
          "};\n"
          "DCP_MODEL(Model)\n")
# error_detail: the library raises while the model is built (an empty domain); the
# driver must report execution_error with the library's own message.
FAILING = ("#include \"dcp.h\"\n"
           "\n"
           "class Model : public dcp::Space {\n"
           " public:\n"
           "  explicit Model(const json& instance) {\n"
           "    int n = instance.at(\"n\");\n"
           "    IntVar x(*this, n, 0);\n"
           "    output(\"x\", x);\n"
           "  }\n"
           "  Model(Model& s) : dcp::Space(s) {}\n"
           "  Gecode::Space* copy() override { return new Model(*this); }\n"
           "};\n"
           "DCP_MODEL(Model)\n")
# stray_stdout: the model prints; the protocol stream must survive it.
CHATTY = ("#include <iostream>\n"
          "#include \"dcp.h\"\n"
          "\n"
          "class Model : public dcp::Space {\n"
          " public:\n"
          "  explicit Model(const json& instance) {\n"
          "    std::cout << \"building the model\" << std::endl;\n"
          "    int n = instance.at(\"n\");\n"
          "    IntVarArray xy(*this, 2, 0, n);\n"
          "    IntVarArgs all;\n"
          "    all << xy[0] << xy[1];\n"
          "    linear(*this, all, IRT_EQ, n);\n"
          "    branch(*this, xy, INT_VAR_SIZE_MIN(), INT_VAL_MIN());\n"
          "    output(\"x\", xy[0]);\n"
          "    output(\"y\", xy[1]);\n"
          "  }\n"
          "  Model(Model& s) : dcp::Space(s) {}\n"
          "  Gecode::Space* copy() override { return new Model(*this); }\n"
          "};\n"
          "DCP_MODEL(Model)\n")
# auxiliary_free_distinct: a free auxiliary variable must not repeat output solutions.
AUXILIARY = ("#include \"dcp.h\"\n"
             "\n"
             "class Model : public dcp::Space {\n"
             " public:\n"
             "  explicit Model(const json& instance) {\n"
             "    int n = instance.at(\"n\");\n"
             "    IntVarArray xy(*this, 2, 0, n);\n"
             "    IntVarArgs all;\n"
             "    all << xy[0] << xy[1];\n"
             "    linear(*this, all, IRT_EQ, n);\n"
             "    IntVar spare(*this, 0, 5);\n"
             "    rel(*this, spare, IRT_GQ, 0);\n"
             "    branch(*this, xy, INT_VAR_SIZE_MIN(), INT_VAL_MIN());\n"
             "    output(\"x\", xy[0]);\n"
             "    output(\"y\", xy[1]);\n"
             "  }\n"
             "  Model(Model& s) : dcp::Space(s) {}\n"
             "  Gecode::Space* copy() override { return new Model(*this); }\n"
             "};\n"
             "DCP_MODEL(Model)\n")
# large_model: 3000 Booleans in one sum, reported as an output.
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
LARGE = ("#include \"dcp.h\"\n"
         "\n"
         "class Model : public dcp::Space {\n"
         " public:\n"
         "  explicit Model(const json& instance) {\n"
         "    int n = instance.at(\"n\");\n"
         "    BoolVarArray b(*this, 3000, 0, 1);\n"
         "    BoolVarArgs all;\n"
         "    for (int i = 0; i < 3000; ++i) all << b[i];\n"
         "    IntVar count = expr(*this, sum(all));\n"
         "    rel(*this, count, IRT_EQ, n);\n"
         "    branch(*this, b, BOOL_VAR_NONE(), BOOL_VAL_MIN());\n"
         "    output(\"b\", b);\n"
         "    output(\"count\", count);\n"
         "  }\n"
         "  Model(Model& s) : dcp::Space(s) {}\n"
         "  Gecode::Space* copy() override { return new Model(*this); }\n"
         "};\n"
         "DCP_MODEL(Model)\n")


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
        check("nested_outputs", NESTED, reference=NESTED_REFERENCE, solution_limit=3)
        check("cloning", CLONING, reference=CLONE_REFERENCE, solution_limit=3)
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
        check("output_shapes", SHAPES, reference=SHAPES_REF)
        check("instance_shapes", SHAPED, reference=SHAPED_REF, instances=[SHAPED_INSTANCE], instance_count=2)
        result = evaluate(candidate("error_detail", FAILING), "readiness", SOLVER, reference_source=REFERENCE)
        results["error_detail"] = (result["reason"] == "execution_error"
                                   and "empty domain" in json.dumps(result).lower())
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
