//! Driver library for the DCP-Bench `pumpkin_rust` integration.
//!
//! A submission is a single Rust file that is `include!`d into a binary crate
//! alongside this library. It defines
//!
//! ```ignore
//! fn build(inst: &Instance, solver: &mut Solver) -> Model
//! ```
//!
//! and nothing else is required of it. `run` reads the evaluator request from
//! stdin, calls `build`, solves, and writes the JSONL runner protocol to stdout:
//! zero or more `solution` records followed by exactly one `status` record.
//!
//! **This library wraps no part of Pumpkin's modelling API.** The `Solver` a
//! submission is handed is `pumpkin_solver::Solver` itself, and constraints are
//! posted with Pumpkin's own constructors. What lives here is the harness with
//! no framework equivalent: reading instance fields out of JSON ([`Instance`]),
//! declaring which variables are the problem's outputs ([`Model`]), and the
//! runner protocol ([`run`]).
//!
//! Everything a submission needs is re-exported from [`prelude`], which the
//! generated binary glob-imports before the submission source.

pub use pumpkin_solver;
pub use serde_json;

use std::io::Read;
use std::time::Duration;
use std::time::Instant;

use serde_json::Map;
use serde_json::Value;
use serde_json::json;

use pumpkin_solver::Solver;
use pumpkin_solver::conflict_resolvers::resolvers::ResolutionResolver;
use pumpkin_solver::core::DefaultBrancher;
use pumpkin_solver::core::optimisation::OptimisationDirection;
use pumpkin_solver::core::optimisation::linear_sat_unsat::LinearSatUnsat;
use pumpkin_solver::core::predicates::Predicate;
use pumpkin_solver::core::predicates::PredicateConstructor;
use pumpkin_solver::core::results::OptimisationResult;
use pumpkin_solver::core::results::ProblemSolution;
use pumpkin_solver::core::results::SatisfactionResult;
use pumpkin_solver::core::results::SolutionReference;
use pumpkin_solver::core::termination::TimeBudget;
use pumpkin_solver::core::variables::AffineView;
use pumpkin_solver::core::variables::DomainId;
use pumpkin_solver::core::variables::Literal;
use pumpkin_solver::core::variables::TransformableVariable;

/// An integer decision variable.
pub type Var = DomainId;
/// A Boolean decision variable. Also usable as a 0/1 integer term.
pub type Lit = Literal;
/// One `coefficient * variable` summand of a linear constraint.
pub type Term = AffineView<DomainId>;

// ---------------------------------------------------------------------------
// Instance
// ---------------------------------------------------------------------------

/// The JSON instance the evaluator supplied, with typed accessors.
///
/// Every accessor panics with the offending key and the value it found rather
/// than substituting a default, so a mismatch between a model and the instance
/// schema shows up as a loud failure instead of a wrong answer.
pub struct Instance {
    root: Value,
}

fn as_i32(value: &Value, what: &str) -> i32 {
    let number = value
        .as_i64()
        .unwrap_or_else(|| panic!("instance field {what}: expected an integer, found {value}"));
    i32::try_from(number)
        .unwrap_or_else(|_| panic!("instance field {what}: {number} does not fit in i32"))
}

impl Instance {
    pub fn new(root: Value) -> Instance {
        Instance { root }
    }

    /// Whether the instance carries this field at all.
    pub fn has(&self, key: &str) -> bool {
        self.root.get(key).is_some()
    }

    /// The raw JSON value of a field.
    pub fn get(&self, key: &str) -> &Value {
        self.root
            .get(key)
            .unwrap_or_else(|| panic!("instance field {key}: missing; instance has {:?}", self.keys()))
    }

    /// Every field name present, sorted.
    pub fn keys(&self) -> Vec<String> {
        match &self.root {
            Value::Object(map) => {
                let mut names: Vec<String> = map.keys().cloned().collect();
                names.sort();
                names
            }
            _ => Vec::new(),
        }
    }

    /// A scalar integer field.
    pub fn int(&self, key: &str) -> i32 {
        as_i32(self.get(key), key)
    }

    /// A scalar integer field, or `fallback` when the instance omits it.
    pub fn int_or(&self, key: &str, fallback: i32) -> i32 {
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
    pub fn ints(&self, key: &str) -> Vec<i32> {
        let value = self.get(key);
        let array = value
            .as_array()
            .unwrap_or_else(|| panic!("instance field {key}: expected an array, found {value}"));
        array
            .iter()
            .enumerate()
            .map(|(i, item)| as_i32(item, &format!("{key}[{i}]")))
            .collect()
    }

    /// A two-dimensional integer array, row-major and not required to be square.
    pub fn matrix(&self, key: &str) -> Vec<Vec<i32>> {
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
                    .map(|(cx, cell)| as_i32(cell, &format!("{key}[{r}][{cx}]")))
                    .collect()
            })
            .collect()
    }

    /// A three-dimensional integer array.
    pub fn cube(&self, key: &str) -> Vec<Vec<Vec<i32>>> {
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
                            .map(|(cx, cell)| as_i32(cell, &format!("{key}[{p}][{r}][{cx}]")))
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
// Declared outputs
// ---------------------------------------------------------------------------

/// One declared output, or a nested array of them.
pub enum Node {
    Int(Var),
    Bool(Lit),
    /// A value the instance already fixes; emitted verbatim.
    ConstInt(i32),
    ConstBool(bool),
    List(Vec<Node>),
}

/// Anything a model can hand to [`Model::put`].
pub trait IntoNode {
    fn node(self) -> Node;
}

impl IntoNode for Var {
    fn node(self) -> Node {
        Node::Int(self)
    }
}

impl IntoNode for Lit {
    fn node(self) -> Node {
        Node::Bool(self)
    }
}

impl IntoNode for i32 {
    fn node(self) -> Node {
        Node::ConstInt(self)
    }
}

impl IntoNode for bool {
    fn node(self) -> Node {
        Node::ConstBool(self)
    }
}

impl IntoNode for Node {
    fn node(self) -> Node {
        self
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

/// Which way an objective is optimised.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Dir {
    Min,
    Max,
}

/// What a submission returns: the declared outputs, and an optional objective.
pub struct Model {
    outputs: Vec<(String, Node)>,
    objective: Option<(Dir, Var)>,
}

impl Default for Model {
    fn default() -> Model {
        Model::new()
    }
}

impl Model {
    pub fn new() -> Model {
        Model {
            outputs: Vec::new(),
            objective: None,
        }
    }

    /// Declare one output under the name the problem brief gives it.
    ///
    /// Panics on a repeated name; the brief never declares the same output twice.
    pub fn put(&mut self, name: &str, value: impl IntoNode) -> &mut Model {
        assert!(
            !self.outputs.iter().any(|(existing, _)| existing == name),
            "output {name} was declared twice"
        );
        self.outputs.push((name.to_string(), value.node()));
        self
    }

    /// Minimise this variable. The runner only reports success once Pumpkin has
    /// *proven* the value optimal.
    pub fn minimise(&mut self, objective: Var) -> &mut Model {
        self.objective = Some((Dir::Min, objective));
        self
    }

    /// Maximise this variable, under the same proof requirement as [`Model::minimise`].
    pub fn maximise(&mut self, objective: Var) -> &mut Model {
        self.objective = Some((Dir::Max, objective));
        self
    }

    fn leaves(&self) -> Vec<&Node> {
        fn walk<'a>(node: &'a Node, out: &mut Vec<&'a Node>) {
            match node {
                Node::List(items) => items.iter().for_each(|item| walk(item, out)),
                leaf => out.push(leaf),
            }
        }
        let mut out = Vec::new();
        for (_, node) in &self.outputs {
            walk(node, &mut out);
        }
        out
    }

    fn render(&self, solution: &SolutionReference<'_>) -> Value {
        fn walk(node: &Node, solution: &SolutionReference<'_>) -> Value {
            match node {
                Node::Int(v) => json!(solution.get_integer_value(*v)),
                Node::Bool(l) => json!(solution.get_integer_value(*l) == 1),
                Node::ConstInt(v) => json!(v),
                Node::ConstBool(b) => json!(b),
                Node::List(items) => Value::Array(items.iter().map(|i| walk(i, solution)).collect()),
            }
        }
        let mut map = Map::new();
        for (name, node) in &self.outputs {
            let _ = map.insert(name.clone(), walk(node, solution));
        }
        Value::Object(map)
    }

    /// A clause that rules out exactly the declared-output values of `solution`,
    /// so the next solve has to differ somewhere a declared output can see.
    ///
    /// Blocking on the declared outputs rather than on the full assignment is
    /// what makes consecutive solutions *distinct as the evaluator sees them*;
    /// two full assignments often agree on every declared output.
    fn blocking_clause(&self, solution: &SolutionReference<'_>) -> Vec<Predicate> {
        self.leaves()
            .into_iter()
            .filter_map(|leaf| match leaf {
                Node::Int(v) => Some(v.disequality_predicate(solution.get_integer_value(*v))),
                Node::Bool(l) => Some(if solution.get_integer_value(*l) == 1 {
                    l.get_false_predicate()
                } else {
                    l.get_true_predicate()
                }),
                _ => None,
            })
            .collect()
    }
}

// ---------------------------------------------------------------------------
// Runner protocol
// ---------------------------------------------------------------------------

fn emit(record: Value) {
    println!("{record}");
}

fn status(kind: &str, detail: &str, seconds: f64) {
    emit(json!({"type": "status", "status": kind, "detail": detail, "solve_seconds": seconds}));
}

struct Budget {
    started: Instant,
    total: f64,
}

impl Budget {
    fn remaining(&self) -> f64 {
        self.total - self.started.elapsed().as_secs_f64()
    }

    fn condition(&self) -> TimeBudget {
        TimeBudget::starting_now(Duration::from_secs_f64(self.remaining().max(0.0)))
    }

    fn spent(&self) -> f64 {
        self.started.elapsed().as_secs_f64()
    }
}

/// Entry point the generated binary calls. Reads the request on stdin, solves,
/// and writes the runner protocol on stdout.
pub fn run(build: fn(&Instance, &mut Solver) -> Model) {
    let mut input = String::new();
    std::io::stdin()
        .read_to_string(&mut input)
        .expect("could not read the request from stdin");
    let request: Value = serde_json::from_str(&input).expect("request was not valid JSON");

    let limit = request["solution_limit"].as_u64().unwrap_or(1) as usize;
    let budget = Budget {
        started: Instant::now(),
        total: request["execution_timeout"].as_f64().unwrap_or(60.0),
    };

    let instance = Instance::new(request["instance"].clone());
    let mut solver = Solver::default();
    let model = build(&instance, &mut solver);

    if model.outputs.is_empty() {
        status("error", "the model declared no outputs", budget.spent());
        return;
    }
    if let Some(declared) = request["outputs"].as_array() {
        let wanted: Vec<&str> = declared.iter().filter_map(|v| v.as_str()).collect();
        let given: Vec<&str> = model.outputs.iter().map(|(name, _)| name.as_str()).collect();
        if !wanted.is_empty() && wanted.iter().any(|name| !given.contains(name)) {
            eprintln!("warning: the brief declares {wanted:?} but the model declared {given:?}");
        }
    }

    let mut brancher = solver.default_brancher();
    let mut resolver = ResolutionResolver::default();
    let mut emitted = 0usize;

    // Optimisation first: establish and prove the optimum, then hold the
    // objective at that value so any further solutions are optimal too.
    if let Some((direction, objective)) = model.objective {
        let mut termination = budget.condition();
        let procedure = LinearSatUnsat::new(
            match direction {
                Dir::Min => OptimisationDirection::Minimise,
                Dir::Max => OptimisationDirection::Maximise,
            },
            objective,
            |_: &Solver, _: SolutionReference, _: &DefaultBrancher, _: &ResolutionResolver| {
                std::ops::ControlFlow::<()>::Continue(())
            },
        );
        let outcome = solver
            .optimise(&mut brancher, &mut termination, &mut resolver, procedure);
        let optimum = match outcome {
            OptimisationResult::Optimal(solution) => solution,
            OptimisationResult::Unsatisfiable => {
                status("unsat", "", budget.spent());
                return;
            }
            // A solution was found but never proven optimal. Reporting it would
            // claim an optimum the solver did not establish.
            OptimisationResult::Satisfiable(_) | OptimisationResult::Stopped(_, _) => {
                status("timeout", "the optimum was not proven", budget.spent());
                return;
            }
            OptimisationResult::Unknown => {
                status("timeout", "", budget.spent());
                return;
            }
        };

        let best = optimum.get_integer_value(objective);
        let reference = optimum.as_reference();
        emit(json!({"type": "solution", "values": model.render(&reference)}));
        emitted = 1;
        if emitted >= limit {
            status("limit", "", budget.spent());
            return;
        }
        let blocking = model.blocking_clause(&reference);
        drop(reference);

        // Fix the objective, then enumerate further solutions at that value.
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::equals(vec![objective.scaled(1)], best, tag))
            .post();
        let tag = solver.new_constraint_tag();
        solver.add_clause(blocking, tag);
    }

    loop {
        if emitted >= limit {
            status("limit", "", budget.spent());
            return;
        }
        if budget.remaining() <= 0.0 {
            status("timeout", "", budget.spent());
            return;
        }
        let mut termination = budget.condition();
        let blocking;
        {
            match solver.satisfy(&mut brancher, &mut termination, &mut resolver)
            {
                SatisfactionResult::Satisfiable(satisfiable) => {
                    let solution = satisfiable.solution();
                    emit(json!({"type": "solution", "values": model.render(&solution)}));
                    emitted += 1;
                    blocking = model.blocking_clause(&solution);
                }
                SatisfactionResult::Unsatisfiable(_, _, _) => {
                    // Exhausted: every remaining assignment repeats a declared
                    // output tuple already emitted.
                    if emitted > 0 {
                        status("complete", "", budget.spent());
                    } else {
                        status("unsat", "", budget.spent());
                    }
                    return;
                }
                SatisfactionResult::Unknown(_, _, _) => {
                    status("timeout", "", budget.spent());
                    return;
                }
            }
        }
        if emitted >= limit {
            status("limit", "", budget.spent());
            return;
        }
        let tag = solver.new_constraint_tag();
        solver.add_clause(blocking, tag);
    }
}

/// Everything a submission needs, glob-imported for it by the generated binary.
pub mod prelude {
    pub use crate::Dir;
    pub use crate::Instance;
    pub use crate::IntoNode;
    pub use crate::Lit;
    pub use crate::Model;
    pub use crate::Node;
    pub use crate::Term;
    pub use crate::Var;
    pub use crate::pumpkin_solver;
    pub use pumpkin_solver::Solver;
    // Pumpkin's own trait for `x.scaled(k)` and `x.offset(k)`, which is how a
    // coefficient is written. In scope here so a model does not have to import
    // it to write a linear constraint.
    pub use pumpkin_solver::core::variables::TransformableVariable;
    pub use serde_json::Value;
    pub use serde_json::json;
}
