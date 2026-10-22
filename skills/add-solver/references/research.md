# What to find out about a solver

Copy into the workspace as `research.md` and fill in. Every answer gets a source (URL + section) or `verified: <file>`. Only the answers an agent would otherwise get wrong end up in the skill.

| Topic | Questions |
|---|---|
| Identity | Package / import name? Solver or modelling framework? Which **native** interfaces does it ship (C++, Python bindings, Java, …), and which do its own docs and examples use? For a framework: which backends, and which is the default? |
| Paradigm | CP / CLP / SAT / MaxSAT / SMT / MIP / ASP / PB? What does a model look like? For SAT/MaxSAT: which integer, cardinality and PB encodings ship with it? |
| Licence | Open source? Free edition without key/account (size-limited, community)? Needs a key, account or registration → **stop and ask the user** |
| Docs | `llms.txt` / `llms-full.txt`? Markdown pages? API reference? Examples directory? |
| Install | Official route for this language? Platform limits (OS, arch, Python/JDK/compiler)? System deps? |
| Verify | Smallest command proving the install works? Installed version? |
| Data input | Reading a data file? Are extra keys (`name`, `note`) an error? Sizes from the data, ragged lists? |
| Variables | Bool, int (domain syntax), interval, set, real? |
| Constraints | Arithmetic beyond linear (`*`, `/`, `%`, `abs`, `min`/`max`)? Exact names of globals (all-different, element, table, cumulative, no-overlap, circuit)? |
| Logic | Reification, implication, disjunction syntax? Indexing an array by a variable? |
| Solve | Call signature? Status values — what is returned on timeout, on infeasible? Reading values? |
| Errors | Where do compile errors, crashes and out-of-memory go: stderr, stdout, a log file, a verbose flag? |
| Objectives | Min / max API? How is proven optimality reported? |
| All solutions | Built-in enumeration or blocking clauses? Duplicates from auxiliary variables? All *optimal* solutions: does the re-posted objective need parentheses? |
| Parameters | Time limit, threads, seed: exact names? Determinism? |
| Reserved words | Keywords that clash with natural names (`matrix`, `E`)? How to rename? |
| Gotchas | Wrong-result issues and a built-in solution checker, 0/1-based indices, overflow, performance traps, recent breaking changes (link the closed issues) |
| Existing skill | Decision from step 1 and why |
