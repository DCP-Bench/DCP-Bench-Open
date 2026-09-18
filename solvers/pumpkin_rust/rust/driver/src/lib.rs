//! Driver library for the DCP-Bench `pumpkin_rust` integration.
//!
//! A submission is a single Rust file that is `include!`d into a binary crate
//! alongside this library. It defines
//!
//! ```ignore
//! fn build(inst: &Instance, cp: &mut Cp) -> Model
//! ```
//!
//! and nothing else is required of it. `run` reads the evaluator request from
//! stdin, calls `build`, solves, and writes the JSONL runner protocol to stdout:
//! zero or more `solution` records followed by exactly one `status` record.
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
use pumpkin_solver::core::proof::ConstraintTag;
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

/// Anything that can appear as a summand in a linear constraint.
///
/// This exists because Pumpkin's linear constraints take a homogeneous slice,
/// so an integer variable and a Boolean have to be widened to a common type.
pub trait IntoTerm {
    fn term(self) -> Term;
}

impl IntoTerm for Var {
    fn term(self) -> Term {
        self.scaled(1)
    }
}

impl IntoTerm for Lit {
    fn term(self) -> Term {
        self.get_integer_variable()
    }
}

impl IntoTerm for Term {
    fn term(self) -> Term {
        self
    }
}

impl<T: IntoTerm + Copy> IntoTerm for &T {
    fn term(self) -> Term {
        (*self).term()
    }
}

/// `1 * v` as a linear summand.
pub fn t(v: impl IntoTerm) -> Term {
    v.term()
}

/// `c * v` as a linear summand.
///
/// A zero coefficient is rejected here rather than passed on. Pumpkin's
/// `AffineView::scaled` multiplies the existing scale without rechecking it, so
/// a zero-scaled view is built happily and then divides by zero inside the
/// propagator. Use [`weighted`], which drops zero-coefficient terms, when the
/// coefficients come from instance data that may contain zeros.
pub fn c(coefficient: i32, v: impl IntoTerm) -> Term {
    assert_ne!(
        coefficient, 0,
        "c(0, ..) has no meaning as a summand; drop the term, or use weighted()"
    );
    v.term().scaled(coefficient)
}

/// Every element as a `1 * v` summand.
pub fn terms<T: IntoTerm + Copy>(vs: &[T]) -> Vec<Term> {
    vs.iter().map(|v| v.term()).collect()
}

/// Element `i` as a `coefficients[i] * vs[i]` summand.
///
/// Panics when the two slices have different lengths, which is a modelling
/// mistake rather than something to silently truncate.
pub fn weighted<T: IntoTerm + Copy>(coefficients: &[i32], vs: &[T]) -> Vec<Term> {
    assert_eq!(
        coefficients.len(),
        vs.len(),
        "weighted(): {} coefficients for {} variables",
        coefficients.len(),
        vs.len()
    );
    // A zero coefficient contributes nothing and cannot be represented: see the
    // note on `c`. Dropping it is the only meaning it could have had.
    coefficients
        .iter()
        .zip(vs)
        .filter(|(&w, _)| w != 0)
        .map(|(&w, v)| v.term().scaled(w))
        .collect()
}

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
// Modelling surface
// ---------------------------------------------------------------------------

/// The solver, plus the constraint helpers a submission builds its model with.
///
/// Each helper allocates its own constraint tag, so a model never has to
/// mention tags. Reach through to [`Cp::solver`] for anything not wrapped here.
pub struct Cp {
    pub solver: Solver,
}

impl Default for Cp {
    fn default() -> Cp {
        Cp::new()
    }
}

impl Cp {
    pub fn new() -> Cp {
        Cp {
            solver: Solver::default(),
        }
    }

    /// A fresh constraint tag, for calling a Pumpkin constraint directly.
    pub fn tag(&mut self) -> ConstraintTag {
        self.solver.new_constraint_tag()
    }

    /// A term list Pumpkin will accept. Filtering zero coefficients can empty a
    /// list entirely, and an empty linear constraint has no propagator to build,
    /// so it becomes `0 <op> rhs` over a variable fixed at zero.
    fn nonempty(&mut self, terms: Vec<Term>) -> Vec<Term> {
        if terms.is_empty() {
            vec![self.constant(0).term()]
        } else {
            terms
        }
    }

    // --- variables ---------------------------------------------------------

    /// An integer variable with domain `[lo, hi]`.
    pub fn int(&mut self, lo: i32, hi: i32) -> Var {
        assert!(lo <= hi, "empty domain [{lo}, {hi}]");
        self.solver.new_bounded_integer(lo, hi)
    }

    /// `n` integer variables with domain `[lo, hi]`.
    pub fn ints(&mut self, n: usize, lo: i32, hi: i32) -> Vec<Var> {
        (0..n).map(|_| self.int(lo, hi)).collect()
    }

    /// A `rows * cols` grid of integer variables with domain `[lo, hi]`.
    pub fn grid(&mut self, rows: usize, cols: usize, lo: i32, hi: i32) -> Vec<Vec<Var>> {
        (0..rows).map(|_| self.ints(cols, lo, hi)).collect()
    }

    /// An integer variable whose domain is exactly `values` (holes allowed).
    pub fn sparse(&mut self, values: &[i32]) -> Var {
        assert!(!values.is_empty(), "sparse domain with no values");
        self.solver.new_sparse_integer(values.to_vec())
    }

    /// A Boolean variable.
    pub fn bool(&mut self) -> Lit {
        self.solver.new_literal()
    }

    /// `n` Boolean variables.
    pub fn bools(&mut self, n: usize) -> Vec<Lit> {
        (0..n).map(|_| self.bool()).collect()
    }

    /// A `rows * cols` grid of Boolean variables.
    pub fn bool_grid(&mut self, rows: usize, cols: usize) -> Vec<Vec<Lit>> {
        (0..rows).map(|_| self.bools(cols)).collect()
    }

    /// A variable fixed to `value`, for places where a constraint wants a
    /// variable but the model has a number.
    pub fn constant(&mut self, value: i32) -> Var {
        self.solver.new_bounded_integer(value, value)
    }

    /// The literal that is always true.
    pub fn always(&mut self) -> Lit {
        self.solver.get_true_literal()
    }

    /// The literal that is always false.
    pub fn never(&mut self) -> Lit {
        self.solver.get_false_literal()
    }

    // --- linear constraints ------------------------------------------------

    /// `sum(terms) == rhs`.
    pub fn eq(&mut self, terms: Vec<Term>, rhs: i32) {
        let terms = self.nonempty(terms);
        let tag = self.tag();
        self.solver
            .add_constraint(pumpkin_solver::equals(terms, rhs, tag))
            .post();
    }

    /// `sum(terms) != rhs`.
    pub fn ne(&mut self, terms: Vec<Term>, rhs: i32) {
        let terms = self.nonempty(terms);
        let tag = self.tag();
        self.solver
            .add_constraint(pumpkin_solver::not_equals(terms, rhs, tag))
            .post();
    }

    /// `sum(terms) <= rhs`.
    pub fn le(&mut self, terms: Vec<Term>, rhs: i32) {
        let terms = self.nonempty(terms);
        let tag = self.tag();
        self.solver
            .add_constraint(pumpkin_solver::less_than_or_equals(terms, rhs, tag))
            .post();
    }

    /// `sum(terms) < rhs`.
    pub fn lt(&mut self, terms: Vec<Term>, rhs: i32) {
        self.le(terms, rhs - 1);
    }

    /// `sum(terms) >= rhs`.
    pub fn ge(&mut self, terms: Vec<Term>, rhs: i32) {
        let negated: Vec<Term> = terms.into_iter().map(|term| term.scaled(-1)).collect();
        self.le(negated, -rhs);
    }

    /// `sum(terms) > rhs`.
    pub fn gt(&mut self, terms: Vec<Term>, rhs: i32) {
        self.ge(terms, rhs + 1);
    }

    /// `sum(terms) == target`, where the right-hand side is itself a variable.
    pub fn sum_eq(&mut self, terms: Vec<Term>, target: impl IntoTerm) {
        let mut all = terms;
        all.push(target.term().scaled(-1));
        self.eq(all, 0);
    }

    /// `sum(terms) <= target`, where the right-hand side is itself a variable.
    pub fn sum_le(&mut self, terms: Vec<Term>, target: impl IntoTerm) {
        let mut all = terms;
        all.push(target.term().scaled(-1));
        self.le(all, 0);
    }

    /// `sum(terms) >= target`, where the right-hand side is itself a variable.
    pub fn sum_ge(&mut self, terms: Vec<Term>, target: impl IntoTerm) {
        let mut all = terms;
        all.push(target.term().scaled(-1));
        self.ge(all, 0);
    }

    /// `a == b`.
    pub fn same(&mut self, a: impl IntoTerm, b: impl IntoTerm) {
        self.eq(vec![a.term(), b.term().scaled(-1)], 0);
    }

    /// `a != b`.
    pub fn differ(&mut self, a: impl IntoTerm, b: impl IntoTerm) {
        self.ne(vec![a.term(), b.term().scaled(-1)], 0);
    }

    /// A fresh variable equal to `sum(terms)`, bounded by the terms' own bounds.
    pub fn sum(&mut self, terms: Vec<Term>) -> Var {
        let lo: i32 = terms.iter().map(|term| self.solver.lower_bound(term)).sum();
        let hi: i32 = terms.iter().map(|term| self.solver.upper_bound(term)).sum();
        let total = self.int(lo, hi);
        self.sum_eq(terms, total);
        total
    }

    // --- arithmetic --------------------------------------------------------

    /// `a * b == product`.
    pub fn times(&mut self, a: impl IntoTerm, b: impl IntoTerm, product: impl IntoTerm) {
        let tag = self.tag();
        self.solver
            .add_constraint(pumpkin_solver::times(a.term(), b.term(), product.term(), tag))
            .post();
    }

    /// `numerator / denominator == quotient`, truncating toward zero.
    ///
    /// Pumpkin requires the denominator's domain to exclude zero.
    pub fn div(&mut self, numerator: impl IntoTerm, denominator: impl IntoTerm, quotient: impl IntoTerm) {
        let tag = self.tag();
        self.solver
            .add_constraint(pumpkin_solver::division(
                numerator.term(),
                denominator.term(),
                quotient.term(),
                tag,
            ))
            .post();
    }

    /// `|signed| == magnitude`.
    pub fn abs(&mut self, signed: impl IntoTerm, magnitude: impl IntoTerm) {
        let tag = self.tag();
        self.solver
            .add_constraint(pumpkin_solver::absolute(signed.term(), magnitude.term(), tag))
            .post();
    }

    /// `max(vars) == target`.
    pub fn max(&mut self, vars: Vec<Term>, target: impl IntoTerm) {
        let tag = self.tag();
        self.solver
            .add_constraint(pumpkin_solver::maximum(vars, target.term(), tag))
            .post();
    }

    /// `min(vars) == target`.
    pub fn min(&mut self, vars: Vec<Term>, target: impl IntoTerm) {
        let tag = self.tag();
        self.solver
            .add_constraint(pumpkin_solver::minimum(vars, target.term(), tag))
            .post();
    }

    // --- global constraints ------------------------------------------------

    /// Every variable takes a different value.
    ///
    /// Pumpkin decomposes this into pairwise disequalities, so it propagates
    /// no more strongly than writing them out.
    pub fn all_different(&mut self, vars: Vec<Term>) {
        let tag = self.tag();
        self.solver
            .add_constraint(pumpkin_solver::all_different(vars, tag))
            .post();
    }

    /// `array[index] == value`, with `index` **0-based**.
    pub fn element(&mut self, index: impl IntoTerm, array: Vec<Term>, value: impl IntoTerm) {
        let tag = self.tag();
        self.solver
            .add_constraint(pumpkin_solver::element(index.term(), array, value.term(), tag))
            .post();
    }

    /// `array[index] == value` for a constant array, with `index` **0-based**.
    pub fn element_of(&mut self, index: impl IntoTerm, array: &[i32], value: impl IntoTerm) {
        let constants: Vec<Term> = array.iter().map(|&v| self.constant(v).term()).collect();
        self.element(index, constants, value);
    }

    /// The assignment to `vars` is one of `rows`.
    pub fn table(&mut self, vars: Vec<Term>, rows: Vec<Vec<i32>>) {
        let tag = self.tag();
        self.solver
            .add_constraint(pumpkin_solver::table(vars, rows, tag))
            .post();
    }

    /// The assignment to `vars` is none of `rows`.
    pub fn forbidden(&mut self, vars: Vec<Term>, rows: Vec<Vec<i32>>) {
        let tag = self.tag();
        self.solver
            .add_constraint(pumpkin_solver::negative_table(vars, rows, tag))
            .post();
    }

    /// Cumulative resource usage never exceeds `capacity`.
    pub fn cumulative(
        &mut self,
        starts: Vec<Term>,
        durations: &[i32],
        demands: &[i32],
        capacity: i32,
    ) {
        assert_eq!(starts.len(), durations.len(), "cumulative(): starts/durations length mismatch");
        assert_eq!(starts.len(), demands.len(), "cumulative(): starts/demands length mismatch");
        let tag = self.tag();
        self.solver
            .add_constraint(pumpkin_solver::cumulative(
                starts,
                durations.to_vec(),
                demands.to_vec(),
                capacity,
                tag,
            ))
            .post();
    }

    // --- Boolean constraints ----------------------------------------------

    /// At least one of `literals` is true.
    pub fn any(&mut self, literals: Vec<Lit>) {
        let tag = self.tag();
        self.solver
            .add_constraint(pumpkin_solver::clause(literals, tag))
            .post();
    }

    /// Every one of `literals` is true.
    pub fn all(&mut self, literals: Vec<Lit>) {
        let tag = self.tag();
        self.solver
            .add_constraint(pumpkin_solver::conjunction(literals, tag))
            .post();
    }

    /// `sum(weights[i] * literals[i]) <= rhs`.
    pub fn bool_le(&mut self, weights: &[i32], literals: &[Lit], rhs: i32) {
        assert_eq!(weights.len(), literals.len(), "bool_le(): weights/literals length mismatch");
        // Pumpkin scales each literal by its weight, so a zero weight reaches
        // the same divide-by-zero as `c(0, ..)`. Drop those pairs.
        let (kept_weights, kept_literals) = keep_nonzero(weights, literals);
        if kept_literals.is_empty() {
            return self.le(Vec::new(), rhs);
        }
        let tag = self.tag();
        self.solver
            .add_constraint(pumpkin_solver::boolean_less_than_or_equals(
                kept_weights,
                kept_literals,
                rhs,
                tag,
            ))
            .post();
    }

    /// `sum(weights[i] * literals[i]) == target`.
    pub fn bool_sum_eq(&mut self, weights: &[i32], literals: &[Lit], target: Var) {
        assert_eq!(weights.len(), literals.len(), "bool_sum_eq(): weights/literals length mismatch");
        let (kept_weights, kept_literals) = keep_nonzero(weights, literals);
        if kept_literals.is_empty() {
            return self.eq(vec![t(target)], 0);
        }
        let tag = self.tag();
        self.solver
            .add_constraint(pumpkin_solver::boolean_equals(
                kept_weights,
                kept_literals,
                target,
                tag,
            ))
            .post();
    }

    /// Exactly `count` of `literals` are true.
    pub fn exactly(&mut self, literals: &[Lit], count: i32) {
        let ones = vec![1; literals.len()];
        let target = self.constant(count);
        self.bool_sum_eq(&ones, literals, target);
    }

    /// At most `count` of `literals` are true.
    pub fn at_most(&mut self, literals: &[Lit], count: i32) {
        let ones = vec![1; literals.len()];
        self.bool_le(&ones, literals, count);
    }

    /// At least `count` of `literals` are true.
    pub fn at_least(&mut self, literals: &[Lit], count: i32) {
        let negated: Vec<Lit> = literals.iter().map(|l| !*l).collect();
        let bound = literals.len() as i32 - count;
        self.at_most(&negated, bound);
    }

    // --- reification -------------------------------------------------------

    /// `flag <-> (sum(terms) == rhs)`.
    pub fn iff_eq(&mut self, flag: Lit, terms: Vec<Term>, rhs: i32) {
        let terms = self.nonempty(terms);
        let tag = self.tag();
        self.solver
            .add_constraint(pumpkin_solver::equals(terms, rhs, tag))
            .reify(flag);
    }

    /// `flag <-> (sum(terms) <= rhs)`.
    pub fn iff_le(&mut self, flag: Lit, terms: Vec<Term>, rhs: i32) {
        let terms = self.nonempty(terms);
        let tag = self.tag();
        self.solver
            .add_constraint(pumpkin_solver::less_than_or_equals(terms, rhs, tag))
            .reify(flag);
    }

    /// `flag <-> (sum(terms) >= rhs)`.
    pub fn iff_ge(&mut self, flag: Lit, terms: Vec<Term>, rhs: i32) {
        let negated: Vec<Term> = terms.into_iter().map(|term| term.scaled(-1)).collect();
        self.iff_le(flag, negated, -rhs);
    }

    /// `flag <-> (v == value)`, the common case of [`Cp::iff_eq`].
    pub fn iff_is(&mut self, flag: Lit, v: impl IntoTerm, value: i32) {
        self.iff_eq(flag, vec![v.term()], value);
    }

    /// A fresh literal that is true exactly when `v == value`.
    pub fn is(&mut self, v: impl IntoTerm, value: i32) -> Lit {
        let flag = self.bool();
        self.iff_is(flag, v, value);
        flag
    }

    /// `flag -> (sum(terms) == rhs)`, leaving the converse free.
    pub fn when_eq(&mut self, flag: Lit, terms: Vec<Term>, rhs: i32) {
        let terms = self.nonempty(terms);
        let tag = self.tag();
        self.solver
            .add_constraint(pumpkin_solver::equals(terms, rhs, tag))
            .implied_by(flag);
    }

    /// `flag -> (sum(terms) <= rhs)`, leaving the converse free.
    pub fn when_le(&mut self, flag: Lit, terms: Vec<Term>, rhs: i32) {
        let terms = self.nonempty(terms);
        let tag = self.tag();
        self.solver
            .add_constraint(pumpkin_solver::less_than_or_equals(terms, rhs, tag))
            .implied_by(flag);
    }

    /// `flag -> (sum(terms) >= rhs)`, leaving the converse free.
    pub fn when_ge(&mut self, flag: Lit, terms: Vec<Term>, rhs: i32) {
        let negated: Vec<Term> = terms.into_iter().map(|term| term.scaled(-1)).collect();
        self.when_le(flag, negated, -rhs);
    }

    // --- bounds ------------------------------------------------------------

    /// The current lower bound of a variable, before search.
    pub fn lower_bound(&self, v: impl IntoTerm) -> i32 {
        self.solver.lower_bound(&v.term())
    }

    /// The current upper bound of a variable, before search.
    pub fn upper_bound(&self, v: impl IntoTerm) -> i32 {
        self.solver.upper_bound(&v.term())
    }
}

/// Split a weighted literal list, dropping every zero-weighted pair.
fn keep_nonzero(weights: &[i32], literals: &[Lit]) -> (Vec<i32>, Vec<Lit>) {
    weights
        .iter()
        .zip(literals)
        .filter(|(&w, _)| w != 0)
        .map(|(&w, &l)| (w, l))
        .unzip()
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
pub fn run(build: fn(&Instance, &mut Cp) -> Model) {
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
    let mut cp = Cp::new();
    let model = build(&instance, &mut cp);

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

    let mut brancher = cp.solver.default_brancher();
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
        let outcome = cp
            .solver
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
        cp.eq(vec![objective.term()], best);
        let tag = cp.tag();
        cp.solver.add_clause(blocking, tag);
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
            match cp
                .solver
                .satisfy(&mut brancher, &mut termination, &mut resolver)
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
        let tag = cp.tag();
        cp.solver.add_clause(blocking, tag);
    }
}

/// Everything a submission needs, glob-imported for it by the generated binary.
pub mod prelude {
    pub use crate::Cp;
    pub use crate::Dir;
    pub use crate::Instance;
    pub use crate::IntoNode;
    pub use crate::IntoTerm;
    pub use crate::Lit;
    pub use crate::Model;
    pub use crate::Node;
    pub use crate::Term;
    pub use crate::Var;
    pub use crate::c;
    pub use crate::t;
    pub use crate::terms;
    pub use crate::weighted;
    pub use crate::pumpkin_solver;
    pub use serde_json::Value;
    pub use serde_json::json;
}
