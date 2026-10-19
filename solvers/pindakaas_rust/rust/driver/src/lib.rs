//! Driver library for the DCP-Bench `pindakaas_rust` integration.
//!
//! A submission is a single Rust file that is `include!`d into a binary crate
//! alongside this library. It defines
//!
//! ```ignore
//! fn build(inst: &Instance, s: &mut Cadical) -> Res<Out>
//! ```
//!
//! and encodes its model into the CaDiCaL solver `s` with Pindakaas's own API
//! (literals, clauses, integer variables, linear, pseudo-Boolean and cardinality
//! constraints) plus the helpers below. Every encoding call returns a `Result`, and
//! the submission propagates each one with `?`: an `Err(Unsatisfiable)` means the
//! formula is already unsatisfiable.
//!
//! This integration is for satisfaction problems only: Pindakaas has no optimiser, and
//! the harness adds none. `run` reads the evaluator request from stdin, solves, and
//! enumerates distinct solutions over the declared outputs with blocking clauses. It
//! writes the JSONL runner protocol to stdout: zero or more `solution` records followed
//! by exactly one `status`.
//!
//! Everything a submission needs is re-exported from [`prelude`].

pub use pindakaas;
pub use serde_json;

use std::io::Read;
use std::sync::Arc;
use std::sync::atomic::{AtomicBool, Ordering};
use std::time::{Duration, Instant};

use pindakaas::constraint::linear::{AdderEncoder, Comparator, LinExp, Linear, LinearEncoder};
use pindakaas::decision::integer::IntVar;
use pindakaas::solver::cadical::Cadical;
use pindakaas::solver::{SolveResult, Solver, TermSignal, TerminateCallback};
use pindakaas::{BoolVal, ClauseDatabase, ClauseDatabaseTools, Lit, Unsatisfiable, Valuation};
use serde_json::Value as Json;
use serde_json::json;

/// The result of encoding. `Err` only ever carries `Unsatisfiable`: the clause database
/// already holds a contradiction, so the problem is infeasible.
pub type Res<T = ()> = Result<T, Unsatisfiable>;

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
// Declared outputs
// ---------------------------------------------------------------------------

/// One declared output leaf, or a nested array of them.
pub enum Node {
    Int(IntVar),
    Bool(Lit),
    ConstInt(i64),
    ConstBool(bool),
    List(Vec<Node>),
    /// `offset + sum 2^i * bits[i]`, least significant bit first.
    Bits(Vec<Lit>, i64),
}

/// A literal handed by reference, as in `out.put("b", &lit)`.
impl IntoNode for &Lit {
    fn node(self) -> Node {
        Node::Bool(*self)
    }
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

impl IntoNode for IntVar {
    fn node(self) -> Node {
        Node::Int(self)
    }
}

impl IntoNode for &IntVar {
    fn node(self) -> Node {
        Node::Int(self.clone())
    }
}

impl IntoNode for Lit {
    fn node(self) -> Node {
        Node::Bool(self)
    }
}

/// A `BoolVal` such as `x.at_least(s, 3)?` is a literal or a constant.
impl IntoNode for BoolVal {
    fn node(self) -> Node {
        match self {
            BoolVal::Lit(l) => Node::Bool(l),
            BoolVal::Const(c) => Node::ConstBool(c),
        }
    }
}

/// A constant the instance already fixes, reported verbatim.
impl IntoNode for i64 {
    fn node(self) -> Node {
        Node::ConstInt(self)
    }
}

/// A constant the instance already fixes, reported verbatim.
impl IntoNode for bool {
    fn node(self) -> Node {
        Node::ConstBool(self)
    }
}

impl<T: IntoNode> IntoNode for Vec<T> {
    fn node(self) -> Node {
        Node::List(self.into_iter().map(IntoNode::node).collect())
    }
}

impl<T: IntoNode + Clone> IntoNode for &[T] {
    fn node(self) -> Node {
        Node::List(self.iter().map(|v| v.clone().node()).collect())
    }
}

impl<T: IntoNode + Clone> IntoNode for &Vec<T> {
    fn node(self) -> Node {
        Node::List(self.iter().map(|v| v.clone().node()).collect())
    }
}

/// What a submission returns: the declared outputs.
pub struct Out {
    outputs: Vec<(String, Node)>,
}

impl Default for Out {
    fn default() -> Out {
        Out::new()
    }
}

impl Out {
    pub fn new() -> Out {
        Out { outputs: Vec::new() }
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

    /// Declare an integer output held in bits: `offset + sum 2^i * bits[i]`, least
    /// significant first. The model constrains the bits itself.
    pub fn put_bits(&mut self, name: &str, bits: Vec<Lit>, offset: i64) -> &mut Out {
        assert!(bits.len() <= 62, "output {name}: {} bits overflow i64", bits.len());
        self.put(name, Node::Bits(bits, offset))
    }
}

/// Number of bits that hold `0..=span`.
fn bits_for(span: i64) -> usize {
    (64 - (span as u64).leading_zeros()) as usize
}

/// A wide integer: `lo + sum 2^i * bits[i]`, least significant bit first. It is not an
/// `IntVar`: a Pindakaas linear constraint over an `IntVar` lists every value of its
/// domain, which aborts past about 10^8 values. Constrain it through [`Wide::exp`] and
/// [`post_wide`], and declare it as an output with `out.put(name, &w)`.
#[derive(Clone, Debug)]
pub struct Wide {
    pub bits: Vec<Lit>,
    pub lo: i64,
}

impl Wide {
    /// The value as a linear expression over the bits (constant `lo` included).
    pub fn exp(&self) -> LinExp {
        let mut e = LinExp::from(self.lo);
        for (i, &b) in self.bits.iter().enumerate() {
            e += LinExp::from(b) * (1i64 << i);
        }
        e
    }
}

/// A fresh wide integer over `lo..=hi`: `bits_for(hi - lo)` literals, with the top of the
/// range cut by one adder constraint.
pub fn wide_int(s: &mut Cadical, lo: i64, hi: i64) -> Res<Wide> {
    assert!(lo < hi, "wide_int({lo}, {hi}): empty or single-valued range");
    let w = Wide { bits: (0..bits_for(hi - lo)).map(|_| s.new_lit()).collect(), lo };
    if hi - lo + 1 != 1i64 << w.bits.len() {
        post_wide(s, w.exp(), Comparator::LessEq, hi)?;
    }
    Ok(w)
}

impl IntoNode for &Wide {
    fn node(self) -> Node {
        assert!(self.bits.len() <= 62, "a wide output of {} bits overflows i64", self.bits.len());
        Node::Bits(self.bits.clone(), self.lo)
    }
}

impl IntoNode for Wide {
    fn node(self) -> Node {
        (&self).node()
    }
}

/// Outputs with more values than this, and no encoding yet, are read and blocked
/// through bits rather than an equality view (a direct encoding, one literal per value).
const WIDE_OUTPUT: usize = 1024;

/// Bits that read an output `x` no constraint has encoded: they become its binary encoding.
fn wide_view(s: &mut Cadical, x: &IntVar) -> Res<Vec<Lit>> {
    let bits: Vec<Lit> = (0..bits_for(x.max() - x.min())).map(|_| s.new_lit()).collect();
    let bv: Vec<BoolVal> = bits.iter().map(|&l| BoolVal::Lit(l)).collect();
    x.with_binary_encoding(s, &bv, x.min(), None)?;
    x.constrain(s)?;
    Ok(bits)
}

// ---------------------------------------------------------------------------
// Helpers: the encodings Pindakaas lacks, and the safe forms of the ones it has
// ---------------------------------------------------------------------------

/// The default linear encoder (MixedRadix for integers, Totalizer for pseudo-Boolean).
fn enc() -> LinearEncoder {
    LinearEncoder::default()
}

/// A `BoolVal` (literal or constant) as a linear term worth 1 when true.
pub fn bx(b: BoolVal) -> LinExp {
    match b {
        BoolVal::Lit(l) => LinExp::from(l),
        BoolVal::Const(c) => LinExp::from(c),
    }
}

/// An integer variable as a linear term.
pub fn iv(x: &IntVar) -> LinExp {
    LinExp::from(x.clone())
}

/// `c * x` as a linear term; empty when `c` is 0. A zero coefficient on an integer
/// term panics inside Pindakaas ("attempt to divide by zero").
pub fn scaled(x: &IntVar, c: i64) -> LinExp {
    if c == 0 { LinExp::default() } else { x.clone() * c }
}

/// Posts `expr <cmp> k`.
///
/// Panics when the coefficients times the variable ranges can reach 2^62: Pindakaas
/// overflows `i64` silently there and drops or accepts constraints it should not.
pub fn post(s: &mut Cadical, e: LinExp, cmp: Comparator, k: i64) -> Res {
    let n = checked(e, k);
    s.encode(&Linear::new(n, cmp, k), &enc())
}

/// Posts `expr <cmp> k` with an adder network. Integer terms enter through their binary
/// encoding (a `wide_int`'s bits), so the cost grows with the logarithm of the ranges,
/// where [`post`] enumerates every value of every integer term. Use it for every
/// constraint that touches a `wide_int`. It propagates weakly, so keep small-domain
/// reasoning on [`post`].
pub fn post_wide(s: &mut Cadical, e: LinExp, cmp: Comparator, k: i64) -> Res {
    let n = checked(e, k);
    s.encode(&Linear::new(n, cmp, k), &LinearEncoder::new(AdderEncoder::default()))
}

/// `e` as one expression, after checking it stays clear of `i64` overflow.
fn checked(e: LinExp, k: i64) -> LinExp {
    let mut n = LinExp::default();
    n += e;
    let mut reach: i128 = (k as i128).abs();
    for (x, c) in n.int_terms() {
        let top = (x.min() as i128).abs().max((x.max() as i128).abs());
        reach += (c as i128).abs() * top;
    }
    for (_, c) in n.bool_terms() {
        reach += (c as i128).abs();
    }
    assert!(
        reach < (1i128 << 62),
        "linear constraint too wide: coefficients times ranges reach {reach}, over 2^62"
    );
    n
}

/// A fresh integer variable `z` with `z == e`, its domain the bounds of `e`. `e` must
/// carry no additive constant. Use it to put an expression behind order or equality
/// literals (`z.at_most(s, k)`, `z.equals(s, k)`).
pub fn define(s: &mut Cadical, e: LinExp) -> Res<IntVar> {
    let mut n = LinExp::default();
    n += e;
    let (mut lo, mut hi) = (0i64, 0i64);
    for (x, c) in n.int_terms() {
        let (a, b) = (c * x.min(), c * x.max());
        lo += a.min(b);
        hi += a.max(b);
    }
    for (_, c) in n.bool_terms() {
        lo += c.min(0);
        hi += c.max(0);
    }
    let z = IntVar::new(lo..=hi);
    post(s, n - iv(&z), Comparator::Equal, 0)?;
    Ok(z)
}

/// A literal for a `BoolVal`: a constant becomes a fresh literal fixed to that value.
pub fn lit_of(s: &mut Cadical, b: BoolVal) -> Res<Lit> {
    match b {
        BoolVal::Lit(l) => Ok(l),
        BoolVal::Const(c) => {
            let l = s.new_lit();
            s.add_clause([if c { l } else { !l }])?;
            Ok(l)
        }
    }
}

/// `conds -> expr <cmp> k`, in the form that is safe over integer terms.
///
/// Pindakaas's own `encode_implied` narrows the domains of the integer variables for
/// good, so a false condition still removes values (silent wrong answers). Here the sum
/// is defined unconditionally as `z`, and only `z`'s order literals sit behind the
/// conditions.
pub fn post_if(s: &mut Cadical, conds: &[Lit], e: LinExp, cmp: Comparator, k: i64) -> Res {
    let z = define(s, e)?;
    let neg: Vec<BoolVal> = conds.iter().map(|&c| BoolVal::Lit(!c)).collect();
    if cmp != Comparator::GreaterEq {
        let l = z.at_most(s, k)?;
        s.add_clause(neg.iter().copied().chain([l]))?;
    }
    if cmp != Comparator::LessEq {
        let l = z.at_least(s, k)?;
        s.add_clause(neg.iter().copied().chain([l]))?;
    }
    Ok(())
}

/// A literal `b` with `b <-> expr <= k`.
pub fn reify_le(s: &mut Cadical, e: LinExp, k: i64) -> Res<Lit> {
    let z = define(s, e)?;
    let l = z.at_most(s, k)?;
    lit_of(s, l)
}

/// A literal `b` with `b <-> expr == k`.
pub fn reify_eq(s: &mut Cadical, e: LinExp, k: i64) -> Res<Lit> {
    let z = define(s, e)?;
    let l = z.equals(s, k)?;
    lit_of(s, l)
}

/// All-different: at most one variable takes each value.
pub fn all_different(s: &mut Cadical, xs: &[IntVar]) -> Res {
    let lo = xs.iter().map(|x| x.min()).min().expect("all_different of nothing");
    let hi = xs.iter().map(|x| x.max()).max().expect("all_different of nothing");
    for v in lo..=hi {
        let mut e = LinExp::default();
        let mut n = 0;
        for x in xs {
            let b = x.equals(s, v)?;
            if b != BoolVal::Const(false) {
                e += bx(b);
                n += 1;
            }
        }
        if n > 1 {
            post(s, e, Comparator::LessEq, 1)?;
        }
    }
    Ok(())
}

/// `c == the number of xs equal to v`.
pub fn count_eq(s: &mut Cadical, xs: &[IntVar], v: i64, c: &IntVar) -> Res {
    let mut e = LinExp::default();
    for x in xs {
        e += bx(x.equals(s, v)?);
    }
    post(s, e - iv(c), Comparator::Equal, 0)
}

/// `r == arr[idx]`, 0-based; `idx` is restricted to the array.
pub fn element_const(s: &mut Cadical, idx: &IntVar, arr: &[i64], r: &IntVar) -> Res {
    post(s, iv(idx), Comparator::GreaterEq, 0)?;
    post(s, iv(idx), Comparator::LessEq, arr.len() as i64 - 1)?;
    for (j, &a) in arr.iter().enumerate() {
        let ij = idx.equals(s, j as i64)?;
        let ra = r.equals(s, a)?;
        s.add_clause([!ij, ra])?;
    }
    Ok(())
}

/// `r == xs[idx]` over variables, 0-based; `idx` is restricted to the array.
pub fn element_var(s: &mut Cadical, idx: &IntVar, xs: &[IntVar], r: &IntVar) -> Res {
    post(s, iv(idx), Comparator::GreaterEq, 0)?;
    post(s, iv(idx), Comparator::LessEq, xs.len() as i64 - 1)?;
    for (j, x) in xs.iter().enumerate() {
        match idx.equals(s, j as i64)? {
            BoolVal::Lit(l) => post_if(s, &[l], iv(x) - iv(r), Comparator::Equal, 0)?,
            BoolVal::Const(true) => post(s, iv(x) - iv(r), Comparator::Equal, 0)?,
            BoolVal::Const(false) => {}
        }
    }
    Ok(())
}

/// Positive table: `xs` takes the values of one of `rows`.
pub fn table(s: &mut Cadical, xs: &[IntVar], rows: &[Vec<i64>]) -> Res {
    let mut pick = LinExp::default();
    for row in rows {
        let t = s.new_lit();
        pick += LinExp::from(t);
        for (x, &v) in xs.iter().zip(row) {
            let e = x.equals(s, v)?;
            s.add_clause([BoolVal::Lit(!t), e])?;
        }
    }
    post(s, pick, Comparator::Equal, 1)
}

/// `m == min(xs)`.
pub fn minimum(s: &mut Cadical, xs: &[IntVar], m: &IntVar) -> Res {
    for x in xs {
        post(s, iv(m) - iv(x), Comparator::LessEq, 0)?;
    }
    for v in (m.min() + 1)..=m.max() {
        let mut cl = vec![m.at_least(s, v)?];
        for x in xs {
            cl.push(!x.at_least(s, v)?);
        }
        s.add_clause(cl)?;
    }
    Ok(())
}

/// `m == max(xs)`.
pub fn maximum(s: &mut Cadical, xs: &[IntVar], m: &IntVar) -> Res {
    for x in xs {
        post(s, iv(m) - iv(x), Comparator::GreaterEq, 0)?;
    }
    for v in m.min()..m.max() {
        let mut cl = vec![m.at_most(s, v)?];
        for x in xs {
            cl.push(!x.at_most(s, v)?);
        }
        s.add_clause(cl)?;
    }
    Ok(())
}

/// `z == x * y`, by cases on the values of `x` (give `x` the smaller domain).
pub fn times(s: &mut Cadical, x: &IntVar, y: &IntVar, z: &IntVar) -> Res {
    let vals: Vec<i64> = x.domain().iter().flatten().collect();
    for a in vals {
        match x.equals(s, a)? {
            BoolVal::Lit(l) => post_if(s, &[l], scaled(y, a) - iv(z), Comparator::Equal, 0)?,
            BoolVal::Const(true) => post(s, scaled(y, a) - iv(z), Comparator::Equal, 0)?,
            BoolVal::Const(false) => {}
        }
    }
    Ok(())
}

/// `r == x mod k` for `x >= 0` and a constant `k > 0`: `x == q*k + r` with `0 <= r < k`.
pub fn mod_const(s: &mut Cadical, x: &IntVar, k: i64, r: &IntVar) -> Res {
    let q = IntVar::new(0..=(x.max() / k));
    post(s, iv(r), Comparator::LessEq, k - 1)?;
    post(s, iv(r), Comparator::GreaterEq, 0)?;
    post(s, iv(&q) * k + iv(r) - iv(x), Comparator::Equal, 0)
}

/// `a == |x|`.
pub fn abs_eq(s: &mut Cadical, x: &IntVar, a: &IntVar) -> Res {
    let neg = x.at_most(s, -1)?;
    let neg = lit_of(s, neg)?;
    post_if(s, &[neg], iv(a) + iv(x), Comparator::Equal, 0)?;
    post_if(s, &[!neg], iv(a) - iv(x), Comparator::Equal, 0)
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

/// Leaves of `node` in declaration order.
fn leaves<'a>(node: &'a Node, found: &mut Vec<&'a Node>) {
    match node {
        Node::List(items) => items.iter().for_each(|item| leaves(item, found)),
        leaf => found.push(leaf),
    }
}

/// Rebuilds the nested shape of `node` from its leaf values, in declaration order.
fn shape<I: Iterator<Item = Json>>(node: &Node, values: &mut I) -> Json {
    match node {
        Node::List(items) => Json::Array(items.iter().map(|item| shape(item, values)).collect()),
        _ => values.next().expect("one value per leaf"),
    }
}

/// Entry point the generated binary calls. Reads the request on stdin, solves, and
/// writes the runner protocol on stdout.
pub fn run(build: fn(&Instance, &mut Cadical) -> Res<Out>) {
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
    let mut s = Cadical::default();
    let out = match build(&instance, &mut s) {
        Ok(out) => out,
        Err(_) => return status("unsat", "the formula is unsatisfiable while it is encoded", elapsed()),
    };
    if out.outputs.is_empty() {
        return status("error", "the model declared no outputs", elapsed());
    }
    let mut flat: Vec<&Node> = Vec::new();
    for (_, node) in &out.outputs {
        leaves(node, &mut flat);
    }

    // `value()` of an integer variable with no encoding is its domain minimum, whatever the
    // model says. Giving each output an equality literal makes it a real, readable variable.
    // A wide output without a direct encoding is read through bits instead: an equality
    // view on it would cost one literal per value and a quadratic at-most-one.
    let mut bits: Vec<Option<(Vec<Lit>, i64)>> = Vec::new();
    for leaf in &flat {
        let view = match leaf {
            Node::Bits(b, offset) => Ok(Some((b.clone(), *offset))),
            Node::Int(x)
                if x.card() > WIDE_OUTPUT
                    && !x.has_direct_encoding()
                    && !x.has_order_encoding()
                    && !x.has_binary_encoding() => {
                wide_view(&mut s, x).map(|b| Some((b, x.min())))
            }
            Node::Int(x) if x.card() > 1 => x.equals(&mut s, x.min()).map(|_| None),
            _ => Ok(None),
        };
        match view {
            Ok(v) => bits.push(v),
            Err(_) => {
                return status("unsat", "the formula is unsatisfiable while the outputs are encoded", elapsed());
            }
        }
    }

    // One terminate callback: the deadline, or enough solutions. Encoding does not poll it.
    let enough = Arc::new(AtomicBool::new(false));
    let stop = enough.clone();
    s.set_terminate_callback(Some(move || {
        if stop.load(Ordering::Relaxed) || Instant::now() >= deadline {
            TermSignal::Terminate
        } else {
            TermSignal::Continue
        }
    }));

    let mut emitted = 0usize;
    let kind = loop {
        if emitted >= limit {
            break "limit";
        }
        // Read the values before touching the solver again: the solution borrows it.
        let row: Result<Option<Vec<Json>>, ()> = match s.solve() {
            SolveResult::Satisfied(sol) => Ok(Some(
                flat.iter()
                    .zip(&bits)
                    .map(|(leaf, view)| match (leaf, view) {
                        (_, Some((b, offset))) => json!(
                            b.iter().enumerate().fold(*offset, |acc, (i, l)| acc
                                + if sol.value(*l) { 1i64 << i } else { 0 })
                        ),
                        (leaf, None) => match leaf {
                        Node::Int(x) => json!(x.value(&sol)),
                        Node::Bool(b) => json!(sol.value(*b)),
                        Node::ConstInt(c) => json!(c),
                        Node::ConstBool(c) => json!(c),
                        Node::Bits(..) | Node::List(_) => unreachable!("bits have a view; lists are flattened"),
                        },
                    })
                    .collect(),
            )),
            SolveResult::Unsatisfiable(_) => Ok(None),
            SolveResult::Unknown => Err(()),
        };
        let values = match row {
            Err(()) => break "timeout",
            Ok(None) => break if emitted > 0 { "complete" } else { "unsat" },
            Ok(Some(values)) => values,
        };

        // Block this assignment of the declared outputs (constants carry no information).
        let mut block: Vec<BoolVal> = Vec::new();
        for ((leaf, value), view) in flat.iter().zip(&values).zip(&bits) {
            match leaf {
                _ if view.is_some() => {
                    let (b, offset) = view.as_ref().unwrap();
                    let v = value.as_i64().expect("integer value") - offset;
                    for (i, l) in b.iter().enumerate() {
                        block.push(BoolVal::Lit(if (v >> i) & 1 == 1 { !*l } else { *l }));
                    }
                }
                Node::Int(x) if x.card() > 1 => {
                    let v = value.as_i64().expect("integer value");
                    block.push(!x.equals(&mut s, v).expect("the value is in the domain"));
                }
                Node::Bool(b) => block.push(BoolVal::Lit(if value.as_bool().expect("Boolean value") { !*b } else { *b })),
                _ => {}
            }
        }
        let mut it = values.into_iter();
        let mut record = serde_json::Map::new();
        for (name, node) in &out.outputs {
            record.insert(name.clone(), shape(node, &mut it));
        }
        println!("{}", json!({"type": "solution", "values": record}));
        emitted += 1;
        if block.is_empty() || s.add_clause(block).is_err() {
            break "complete";
        }
    };
    enough.store(true, Ordering::Relaxed);
    status(kind, "", elapsed());
}

/// Everything a submission needs, glob-imported for it by the generated binary.
pub mod prelude {
    pub use crate::{
        Instance, IntoNode, Node, Out, Res, abs_eq, all_different, bx, count_eq, define, element_const,
        element_var, iv, lit_of, maximum, minimum, mod_const, post, post_if, post_wide, reify_eq, reify_le, scaled,
        table, times, wide_int, Wide,
    };
    pub use pindakaas;
    pub use pindakaas::RangeList;
    pub use pindakaas::constraint::linear::{AdderEncoder, Comparator, LinExp, Linear, LinearEncoder, StaticLinEncoder};
    pub use pindakaas::constraint::propositional_logic::{Formula, TseitinEncoder};
    pub use pindakaas::decision::integer::IntVar;
    pub use pindakaas::solver::cadical::Cadical;
    pub use pindakaas::{BoolVal, ClauseDatabase, ClauseDatabaseTools, Lit, Unsatisfiable};
    pub use serde_json::Value;
    pub use serde_json::json;
}
