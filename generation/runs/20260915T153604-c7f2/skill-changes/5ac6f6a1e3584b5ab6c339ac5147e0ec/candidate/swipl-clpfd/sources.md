# Sources for `swipl-clpfd`

Documentation this skill's instructions were written from. Add an entry whenever
a claim here comes from a specific page or version.

- <https://www.swi-prolog.org/pldoc/man?section=clpfd> — library(clpfd) reference, accessed 2026-09-14
- <https://www.swi-prolog.org/pldoc/doc_for?object=labeling/2> — labeling/2 and its option categories, accessed 2026-09-14
- <https://hub.docker.com/_/swipl> — `swipl:9.2.9`, the image this integration builds on

Every constraint in the API tables and every idiom in this skill was checked by
running SWI-Prolog 9.2.9 inside the integration image, not taken from
documentation alone:

- `all_distinct/1`, `all_different/1`, `sum/3`, `scalar_product/4`,
  `element/3`, `global_cardinality/2`, `circuit/1`, `tuples_in/2`,
  `lex_chain/1`, `chain/2`, `serialized/2`, `disjoint2/1`,
  `cumulative/2` with `task/5` and `limit/1`, `automaton/3` and `transpose/2`
  all resolve and propagate as described.
- `element/3` is 1-based and accepts a variable index, which is what makes the
  flatten-and-index idiom the way to read a matrix cell chosen by a decision
  variable. `nth0/3` and `nth1/3` need an integer index.
- There is no `nvalue/2` and no `count/4` in SWI-Prolog's clpfd; counting goes
  through `#<==>` reification plus `sum/3`, or `global_cardinality/2` with a
  variable count, both of which were run.
- Expression operators `+ - * // div mod rem abs min max ^` and domain unions
  such as `X in 1..3 \/ 7..9` were each checked on a small goal.
- `labeling([min(Expr)], Vars)` enumerates in ascending order of `Expr`, so the
  first solution carries the optimum. The integration's driver relies on this
  and re-solves with the optimum fixed before enumerating, so an unproven
  optimum can never be reported as a result.
- Labelling an unbounded variable raises
  `Arguments are not sufficiently instantiated`, which is why the skill insists
  on `ins`/`in` before labelling.
- JSON instances reach a model as a dict through `json_read_dict/3` with
  `value_string_as(atom)`: arrays become lists, nested arrays lists of lists,
  and strings atoms. A matrix output serialises back as a nested JSON array on
  one line, including under an uppercase declared name such as `'A'`.
