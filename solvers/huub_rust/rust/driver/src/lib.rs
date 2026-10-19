//! Driver library for the DCP-Bench `huub_rust` integration.
//!
//! A submission is a single Rust file that is `include!`d into a binary crate
//! alongside this library. It defines
//!
//! ```ignore
//! fn build(inst: &Instance, m: &mut Model) -> Res<Out>
//! ```
//!
//! and posts its constraints on `m` with Huub's own modelling API. Every `post()`
//! returns a `Result`, and the submission propagates each one with `?`: an `Err`
//! means that constraint already conflicts, so the problem is infeasible.
//!
//! `run` reads the evaluator request from stdin, lowers the model, proves the
//! optimum when the submission declares an objective, then enumerates distinct
//! solutions over the declared outputs. It writes the JSONL runner protocol to
//! stdout: zero or more `solution` records followed by exactly one `status`.
//!
//! Everything a submission needs is re-exported from [`prelude`].

pub use huub;
pub use serde_json;

use std::cell::Cell;
use std::io::Read;
use std::rc::Rc;
use std::time::{Duration, Instant};

use huub::actions::IntDecisionActions;
use huub::constraints::Conflict;
use huub::lower::LoweringMap;
use huub::model::expressions::IntLinearExp;
use huub::model::{Model, View};
use huub::solver::{AnyView, IntLitMeaning, Solver, Status, TerminationSignal, Valuation, Value};
use serde_json::Value as Json;
use serde_json::json;

/// The result of building a model. `Err` only ever carries a conflict from a `post()`.
pub type Res<T> = Result<T, Conflict<View<bool>>>;

// ---------------------------------------------------------------------------
// Instance
// ---------------------------------------------------------------------------

/// The JSON instance the evaluator supplied, with typed accessors.
///
/// Every accessor panics with the offending key and the value it found rather
/// than substituting a default, so a mismatch between a model and the instance
/// schema shows up as a loud failure instead of a wrong answer.
pub struct Instance {
    root: Json,
}

fn as_i64(value: &Json, what: &str) -> i64 {
    value
        .as_i64()
        .unwrap_or_else(|| panic!("instance field {what}: expected an integer, found {value}"))
}

impl Instance {
    pub fn new(root: Json) -> Instance {
        Instance { root }
    }

    /// Whether the instance carries this field at all.
    pub fn has(&self, key: &str) -> bool {
        self.root.get(key).is_some()
    }

    /// The raw JSON value of a field.
    pub fn get(&self, key: &str) -> &Json {
        self.root
            .get(key)
            .unwrap_or_else(|| panic!("instance field {key}: missing; instance has {:?}", self.keys()))
    }

    /// Every field name present, sorted.
    pub fn keys(&self) -> Vec<String> {
        match &self.root {
            Json::Object(map) => {
                let mut names: Vec<String> = map.keys().cloned().collect();
                names.sort();
                names
            }
            _ => Vec::new(),
        }
    }

    /// A scalar integer field.
    pub fn int(&self, key: &str) -> i64 {
        as_i64(self.get(key), key)
    }

    /// A scalar integer field, or `fallback` when the instance omits it.
    pub fn int_or(&self, key: &str, fallback: i64) -> i64 {
        if self.has(key) { self.int(key) } else { fallback }
    }

    /// A scalar integer field as `usize`, for sizes and counts.
    pub fn size(&self, key: &str) -> usize {
        let value = self.int(key);
        usize::try_from(value)
            .unwrap_or_else(|_| panic!("instance field {key}: {value} is not a valid size"))
    }

    /// A scalar Boolean field.
    pub fn flag(&self, key: &str) -> bool {
        let value = self.get(key);
        value
            .as_bool()
            .unwrap_or_else(|| panic!("instance field {key}: expected a Boolean, found {value}"))
    }

    /// A one-dimensional integer array.
    pub fn ints(&self, key: &str) -> Vec<i64> {
        let value = self.get(key);
        let array = value
            .as_array()
            .unwrap_or_else(|| panic!("instance field {key}: expected an array, found {value}"));
        array
            .iter()
            .enumerate()
            .map(|(i, item)| as_i64(item, &format!("{key}[{i}]")))
            .collect()
    }

    /// A two-dimensional integer array, row-major and not required to be square.
    pub fn matrix(&self, key: &str) -> Vec<Vec<i64>> {
        let value = self.get(key);
        let rows = value
            .as_array()
            .unwrap_or_else(|| panic!("instance field {key}: expected an array of arrays, found {value}"));
        rows.iter()
            .enumerate()
            .map(|(r, row)| {
                let cells = row.as_array().unwrap_or_else(|| {
                    panic!("instance field {key}[{r}]: expected an array, found {row}")
                });
                cells
                    .iter()
                    .enumerate()
                    .map(|(cx, cell)| as_i64(cell, &format!("{key}[{r}][{cx}]")))
                    .collect()
            })
            .collect()
    }

    /// A three-dimensional integer array.
    pub fn cube(&self, key: &str) -> Vec<Vec<Vec<i64>>> {
        let value = self.get(key);
        let planes = value
            .as_array()
            .unwrap_or_else(|| panic!("instance field {key}: expected a 3-D array, found {value}"));
        planes
            .iter()
            .enumerate()
            .map(|(p, plane)| {
                let rows = plane.as_array().unwrap_or_else(|| {
                    panic!("instance field {key}[{p}]: expected an array, found {plane}")
                });
                rows.iter()
                    .enumerate()
                    .map(|(r, row)| {
                        let cells = row.as_array().unwrap_or_else(|| {
                            panic!("instance field {key}[{p}][{r}]: expected an array, found {row}")
                        });
                        cells
                            .iter()
                            .enumerate()
                            .map(|(cx, cell)| as_i64(cell, &format!("{key}[{p}][{r}][{cx}]")))
                            .collect()
                    })
                    .collect()
            })
            .collect()
    }

    /// A one-dimensional array of strings.
    pub fn strings(&self, key: &str) -> Vec<String> {
        let value = self.get(key);
        let array = value
            .as_array()
            .unwrap_or_else(|| panic!("instance field {key}: expected an array, found {value}"));
        array
            .iter()
            .enumerate()
            .map(|(i, item)| {
                item.as_str()
                    .unwrap_or_else(|| panic!("instance field {key}[{i}]: expected a string, found {item}"))
                    .to_string()
            })
            .collect()
    }

    /// A one-dimensional array of Booleans.
    pub fn flags(&self, key: &str) -> Vec<bool> {
        let value = self.get(key);
        let array = value
            .as_array()
            .unwrap_or_else(|| panic!("instance field {key}: expected an array, found {value}"));
        array
            .iter()
            .enumerate()
            .map(|(i, item)| {
                item.as_bool()
                    .unwrap_or_else(|| panic!("instance field {key}[{i}]: expected a Boolean, found {item}"))
            })
            .collect()
    }

    /// The length of an array field.
    pub fn len(&self, key: &str) -> usize {
        let value = self.get(key);
        value
            .as_array()
            .unwrap_or_else(|| panic!("instance field {key}: expected an array, found {value}"))
            .len()
    }
}

// ---------------------------------------------------------------------------
// Declared outputs and objective
// ---------------------------------------------------------------------------

/// One declared output leaf, or a nested array of them.
pub enum Node {
    Int(View<i64>),
    Bool(View<bool>),
    List(Vec<Node>),
}

/// Anything a submission can hand to [`Out::put`].
pub trait IntoNode {
    fn node(self) -> Node;
}

impl IntoNode for Node {
    fn node(self) -> Node {
        self
    }
}

impl IntoNode for View<i64> {
    fn node(self) -> Node {
        Node::Int(self)
    }
}

impl IntoNode for View<bool> {
    fn node(self) -> Node {
        Node::Bool(self)
    }
}

/// A constant the instance already fixes, reported verbatim.
impl IntoNode for i64 {
    fn node(self) -> Node {
        Node::Int(self.into())
    }
}

/// A constant the instance already fixes, reported verbatim.
impl IntoNode for bool {
    fn node(self) -> Node {
        Node::Bool(self.into())
    }
}

impl<T: IntoNode> IntoNode for Vec<T> {
    fn node(self) -> Node {
        Node::List(self.into_iter().map(IntoNode::node).collect())
    }
}

impl<T: IntoNode + Copy> IntoNode for &[T] {
    fn node(self) -> Node {
        Node::List(self.iter().map(|v| (*v).node()).collect())
    }
}

impl<T: IntoNode + Copy> IntoNode for &Vec<T> {
    fn node(self) -> Node {
        Node::List(self.iter().map(|v| (*v).node()).collect())
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum Dir {
    Min,
    Max,
}

/// What a submission returns: the declared outputs, and an optional objective.
pub struct Out {
    outputs: Vec<(String, Node)>,
    objective: Option<(Dir, View<i64>)>,
}

impl Default for Out {
    fn default() -> Out {
        Out::new()
    }
}

impl Out {
    pub fn new() -> Out {
        Out {
            outputs: Vec::new(),
            objective: None,
        }
    }

    /// Declare one output under the name the problem brief gives it.
    ///
    /// Panics on a repeated name; the brief never declares the same output twice.
    pub fn put(&mut self, name: &str, value: impl IntoNode) -> &mut Out {
        assert!(
            !self.outputs.iter().any(|(existing, _)| existing == name),
            "output {name} was declared twice"
        );
        self.outputs.push((name.to_string(), value.node()));
        self
    }

    /// Minimise this integer view. The runner only reports success once Huub has
    /// proven the value optimal.
    pub fn minimise(&mut self, objective: View<i64>) -> &mut Out {
        self.objective = Some((Dir::Min, objective));
        self
    }

    /// Maximise this integer view, under the same proof requirement as [`Out::minimise`].
    pub fn maximise(&mut self, objective: View<i64>) -> &mut Out {
        self.objective = Some((Dir::Max, objective));
        self
    }
}

// ---------------------------------------------------------------------------
// Helpers for constructs Huub lacks or mishandles
// ---------------------------------------------------------------------------

/// Posts `expr == rhs` as `expr <= rhs` and `expr >= rhs`.
///
/// Use it for an equality over two terms, or with a coefficient other than 1
/// (see the traps in `CONTRACT.md`): `m.linear(..).eq(..)` on those hangs or
/// exhausts memory on large domains, and the two bounds post cleanly.
pub fn eq2(m: &mut Model, expr: impl Into<IntLinearExp> + Clone, rhs: i64) -> Res<()> {
    m.linear(expr.clone()).le(rhs).post()?;
    m.linear(expr).ge(rhs).post()?;
    Ok(())
}

/// The sum of `x == v` over `xs`, as a linear expression: the number of entries
/// equal to `v`. Post it with `m.linear(count_eq(&xs, v)).eq(k)`.
pub fn count_eq(xs: &[View<i64>], v: i64) -> IntLinearExp {
    xs.iter().map(|x| x.eq(v)).sum()
}

/// Posts that `next` is a single Hamiltonian circuit over `0..next.len()`:
/// `next[i]` is the successor of node `i`, with no fixed points.
///
/// Huub has no circuit constraint, so this uses the standard decomposition: all
/// successors differ, and a visiting order starting at node 0 follows `next`
/// through every node. `next` must have domain `0..=n-1`, with `n >= 2`.
pub fn circuit(m: &mut Model, next: &[View<i64>]) -> Res<()> {
    let n = next.len();
    let next_vec: Vec<View<i64>> = next.to_vec();
    let order = m.new_int_decisions(n, 0..=(n as i64 - 1));
    m.unique(next_vec.clone()).post()?;
    m.unique(order.clone()).post()?;
    m.linear(order[0]).eq(0).post()?;
    for (i, succ) in next_vec.iter().enumerate() {
        m.linear(*succ).ne(i as i64).post()?;
    }
    for k in 0..n - 1 {
        m.element(next_vec.clone()).index(order[k]).result(order[k + 1]).post()?;
    }
    m.element(next_vec).index(order[n - 1]).result(order[0]).post()?;
    Ok(())
}

// ---------------------------------------------------------------------------
// Runner protocol
// ---------------------------------------------------------------------------

fn status(kind: &str, detail: &str, seconds: f64) {
    println!(
        "{}",
        json!({"type": "status", "status": kind, "detail": detail, "solve_seconds": seconds})
    );
}

/// Pushes the leaf views of `node` in declaration order.
fn lower_node(node: &Node, map: &LoweringMap, solver: &mut Solver, views: &mut Vec<AnyView>) {
    match node {
        Node::Int(v) => views.push(AnyView::Int(map.get(solver, *v))),
        Node::Bool(b) => views.push(AnyView::Bool(map.get(solver, *b))),
        Node::List(items) => items
            .iter()
            .for_each(|item| lower_node(item, map, solver, views)),
    }
}

/// Rebuilds the nested shape of `node` from its leaf values, in declaration order.
fn shape<I: Iterator<Item = Json>>(node: &Node, leaves: &mut I) -> Json {
    match node {
        Node::Int(_) | Node::Bool(_) => leaves.next().expect("one value per leaf"),
        Node::List(items) => Json::Array(items.iter().map(|item| shape(item, leaves)).collect()),
    }
}

fn solution_record(out: &Out, leaves: Vec<Json>) -> Json {
    let mut values = serde_json::Map::new();
    let mut leaves = leaves.into_iter();
    for (name, node) in &out.outputs {
        values.insert(name.clone(), shape(node, &mut leaves));
    }
    json!({"type": "solution", "values": values})
}

/// Entry point the generated binary calls. Reads the request on stdin, solves,
/// and writes the runner protocol on stdout.
pub fn run(build: fn(&Instance, &mut Model) -> Res<Out>) {
    let started = Instant::now();
    let elapsed = || started.elapsed().as_secs_f64();

    let mut input = String::new();
    std::io::stdin()
        .read_to_string(&mut input)
        .expect("could not read the request from stdin");
    let request: Json = serde_json::from_str(&input).expect("request was not valid JSON");
    let limit = request["solution_limit"].as_u64().unwrap_or(1) as usize;
    let total = request["execution_timeout"].as_f64().unwrap_or(60.0);
    let deadline = started + Duration::from_secs_f64(total);

    let instance = Instance::new(request["instance"].clone());
    let mut model = Model::default();
    let out = match build(&instance, &mut model) {
        Ok(out) => out,
        Err(_) => return status("unsat", "a constraint conflicts when it is posted", elapsed()),
    };
    if out.outputs.is_empty() {
        return status("error", "the model declared no outputs", elapsed());
    }

    // A conflict found while simplifying or lowering is infeasibility, like a
    // conflict at post time; any other failure is a panic and reports as `error`.
    let (mut solver, map): (Solver, _) = match model.lower().to_solver() {
        Ok(lowered) => lowered,
        Err(_) => return status("unsat", "the model is infeasible during lowering", elapsed()),
    };
    let mut views = Vec::new();
    for (_, node) in &out.outputs {
        lower_node(node, &map, &mut solver, &mut views);
    }
    let objective = out
        .objective
        .map(|(dir, view)| (dir, map.get(&mut solver, view)));

    // One terminate callback for both phases: the deadline, or enough solutions.
    let enough = Rc::new(Cell::new(false));
    let stop = enough.clone();
    solver.set_terminate_callback(Some(move || {
        if stop.get() || Instant::now() >= deadline {
            TerminationSignal::Terminate
        } else {
            TerminationSignal::Continue
        }
    }));

    // Phase 1: prove the optimum. `minimize`/`maximize` must be the first solve on
    // this solver; a later bound query reports a stale value.
    let mut pin = None;
    if let Some((dir, objective)) = objective {
        let (outcome, best) = match dir {
            Dir::Min => solver.solve().minimize(objective),
            Dir::Max => solver.solve().maximize(objective),
        };
        match (outcome, best) {
            (Status::Complete, Some(value)) => {
                pin = Some(objective.lit(&mut solver, IntLitMeaning::Eq(value)));
            }
            (Status::Unsatisfiable, _) => return status("unsat", "", elapsed()),
            (Status::Satisfied, Some(_)) => {
                return status("timeout", "the optimum was not proven", elapsed());
            }
            _ => return status("timeout", "", elapsed()),
        }
    }

    // Phase 2: enumerate distinct solutions over the declared outputs, with the
    // objective pinned to its optimum when there is one. The solver can run past
    // the cap between solutions, so extra rows are dropped here.
    let mut emitted = 0usize;
    let outcome = solver
        .solve()
        .assuming(pin)
        .all_solutions(views.clone())
        .on_solution(|sol| {
            if emitted < limit {
                let leaves: Vec<Json> = views
                    .iter()
                    .map(|view| match view.val(sol) {
                        Value::Int(i) => json!(i),
                        Value::Bool(b) => json!(b),
                    })
                    .collect();
                println!("{}", solution_record(&out, leaves));
                emitted += 1;
                if emitted >= limit {
                    enough.set(true);
                }
            }
        })
        .satisfy();

    let kind = match outcome {
        Status::Satisfied if emitted >= limit => "limit",
        Status::Satisfied | Status::Unknown => "timeout",
        Status::Complete | Status::Unsatisfiable if emitted > 0 => "complete",
        Status::Complete | Status::Unsatisfiable => "unsat",
    };
    status(kind, "", elapsed());
}

/// Everything a submission needs, glob-imported for it by the generated binary.
pub mod prelude {
    pub use crate::{Instance, IntoNode, Node, Out, Res, circuit, count_eq, eq2};
    pub use huub::Set;
    pub use huub::constraints::Conflict;
    pub use huub::model::expressions::{BoolFormula, IntLinearExp};
    pub use huub::model::{Model, View};
    pub use serde_json::Value;
    pub use serde_json::json;
}
