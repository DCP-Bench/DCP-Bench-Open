# clingo_asp: underscore field names and per-character string facts

## What changed

`solvers/clingo_asp/run.py`:

1. `predicate()` keeps leading underscores and lowers the first character after
   them: `_SHIP` -> `_sHIP`, `_x` -> `_x`, `__Ab` -> `__ab`. For a name without a
   leading underscore the result is identical to before (`N` -> `n`,
   `MAX_STEPS` -> `mAX_STEPS`). The same function maps declared outputs, so `_A`
   is carried by `_a`. Collisions are still refused.
2. Every string value, at any depth, adds facts
   `<pred>_char(index, ..., position, "c")`: the list indices of the string,
   then the 0-based character position, then the character as a one-character
   string, escaped by the same `term()` as the whole-string fact. The existing
   `<pred>(index, ..., "string")` fact is unchanged. If `<pred>_char` is the
   predicate of another field in the same instance, the instance is refused.

`solvers/clingo_asp/readiness_test.py`: two checks added, `underscore_field`
(reference field `_N`, model reads `_n/1`, changed instance `_N = 3`) and
`string_characters` (string and list of strings; word lengths and the alphabet
position of each word's last letter, changed instance with other strings).
Every existing check kept.

Modelling skill (`solvers/clingo_asp/skills/clingo-asp/`): both rules, a worked
example, a gotcha on `name`/`note` metadata facts and on unparseable string
escapes, sources entries, and the eval scenario `string-and-underscore-fields`.

## Why

Blockers `building_blocks` (strings cannot be split in plain ASP; `#script`
unavailable) and `csplib_014_solitaire_battleships` (`_SHIP(1).` is a variable,
"parsing failed").

`building_blocks` fields as they reach the runner (measured from the dataset
JSON and `embedded_instance` of the reference): `alphabet` is a string and
`words_str` is a JSON list of strings (`["BAKE", "ONYX", ...]`), not one string
holding a Python-style list. It arrives as `words_str(0,"BAKE")` and now also as
`words_str_char(0,0,"B")` and so on.

## Evidence

- `new-checks-before-rebuild.json`: both new checks fail on the old image
  (`sha256:b81127693c3a...`): `parsing failed`, and no `last/N` atoms.
- `build.log`, `image-id.txt`: rebuilt image
  `sha256:b8c3afb2ead29f8d522c4371230ed2df58cfc86a22e6b9128655f52716141a0c`.
- `readiness-script.stdout/.stderr`: all 12 checks true.
- `readiness-check.log`, `readiness-verify.log`: record written to
  `solvers/clingo_asp/readiness.json` with evidence in
  `solvers/clingo_asp/readiness/`; verify accepted. The previous record is
  archived at `solvers/clingo_asp/readiness/superseded/readiness-before-character-facts.json`.
- `facts-comparison.json`: old and new `facts()` over all 757 dataset instances
  (embedded examples and listed instances). Outside `*_char` lines the output is
  line-for-line identical everywhere except the five
  `csplib_014_solitaire_battleships` listed instances (`_SHIP` renamed). No
  instance errors under one version and not the other. 402 instances gain
  `_char` facts (mostly from `name`/`note`).
- `building-blocks-recovery.txt`: inside the image, the new facts plus
  `word_letter(W,P,L) :- words_str_char(W,P,C), alphabet_char(L,C).` and a
  `#count` length rebuild every word of all 5 `building_blocks` instances
  exactly.
- `worked-example.txt`: the skill's worked example run in the image, the
  naming rule on sample names, and both refusals.
- `tests.log`: `tests/test_solvers.py` MetadataTests (7) and the clingo_asp
  subtests of ContainerTests `test_pilots` and `test_maximization`, plus
  `test_missing_image`, with `DCP_CONTAINER_TESTS=1`: all pass.
- `reevaluation/`, `reevaluation-summary.jsonl`: 24 retained models over 20
  problems re-evaluated on the rebuilt image (`--instance-count 99
  --solution-limit 2`, 180 s timeouts): all 24 accepted on every available
  instance. The sample holds every retained model whose problem has string
  fields (cabling, facility_location, room_assignment,
  session2_movie_scheduling, who_killed_agatha), every one with capitalised
  field names (9 problems), and 10 more; the 5-instance problems carry
  `name`/`note` strings, so they also exercise the new `_char` facts.
- Survey of all 168 retained models: none contains an identifier ending in
  `_char`; none belongs to a problem with an underscore-prefixed field; none of
  their instances has a non-ASCII or tab character.

## Not verified

- Retained models outside the re-evaluation sample were not re-run. Their facts
  are unchanged except for added `*_char` facts, and no retained model mentions
  a `_char` predicate, so they ground the same rules over extra unused facts.
- A string containing a tab or a non-ASCII character still fails to parse,
  because `term()` uses `json.dumps` escapes (`\t`, `\uXXXX`) that clingo
  rejects. This predates the change and was left alone so existing facts stay
  byte-identical; no dataset instance contains such a character today.
- `evaluation/README.md` (Runner protocol) still says clingo_asp lowers the
  first character; it was not edited because the evaluator directory was out of
  scope.
- No building_blocks or csplib_014 model was written.
