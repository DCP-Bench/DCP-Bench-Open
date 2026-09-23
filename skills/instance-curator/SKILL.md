---
name: instance-curator
description: Add instances to DCP-Bench Open problems that already read their data from a data section. Find published instances or generate them, gate each one (right fields and shapes, distinct, satisfiable, solved or proven optimal by the reference within 10 seconds), append the ones that pass, and recheck every retained model on them, flagging the models they disprove. Use for campaigns that grow the evaluation instances, or to add a single instance to one problem.
---

# Instance curator

A retained model was accepted on the instances its problem had at the time.
Each instance added later is another chance to catch a model that fitted those
and nothing else. An instance is worth adding when a correct model can pass it
and a wrong model might not. One that is unsatisfiable, too slow to check, or a
disguised copy of an existing instance adds cost and no test.

You need this repository and its Python environment (`.venv/Scripts/python.exe`
on Windows, `.venv/bin/python` on Unix). The recheck step also needs a running
Docker Linux engine with the integration images built (`python -m
evaluation.build`). Run every command from the repository root. An unavailable
engine is a blocker to report. Never skip the recheck because of it.

## The loop

```sh
git switch -c instances/<batch>                    # never commit to main, never push
python -m generation.instances status              # what can take more instances
python -m generation.brief PROBLEM                 # the fields and their shapes
#   read the reference and its description; write candidates to a scratch file
python -m generation.instances check PROBLEM candidates.json
python -m generation.instances check PROBLEM candidates.json --append
python -m generation.instances recheck PROBLEM --instances json:K ... --jobs 4
python -m generation.instances recheck PROBLEM --instances json:K ... --flag   # once you have decided
python -W ignore::SyntaxWarning -m unittest tests.test_evaluation
#   commit the batch, then take the next problem
```

1. **Branch first.** One branch per batch, named `instances/<batch>`, created
   off whatever branch you are on. If the checkout has uncommitted work, stop
   and ask.
2. **Pick the problem.** `status` lists problems with fewer than 5 distinct
   instances, fewest first. Among equal counts it puts the problems with more
   retained models first, since a new instance there rechecks more of them. It
   leaves out the problems under "Instances not added" in `SOURCES.md`. It also
   leaves out problems with no data fields, whose data is written into the
   model itself. Adding an instance to one of those means rewriting its
   reference, which is out of scope here.
3. **Read the problem before looking for data.** Read the description, the
   reference (`dataset/<problem>/<problem>.cpmpy.py`) and `generation.brief`.
   Then decide whether the problem can take another instance at all.
   - The description is the text a model is written from, and a new instance
     must not contradict it. A value the description states is fixed for
     every instance. Sudoku's description says "a 9x9 grid", so a new sudoku
     is another 9x9 puzzle, never a 16x16 one. When the description pins down
     all of the data (the clues of one specific puzzle, the full table of one
     scenario), no second instance fits. Record the problem under "Instances
     not added" (below) and move on. On 2026-09-23, 20 of the 97 problems with
     only the example had a description containing one of the example's
     numbers. That was a numeric search, which misses numbers written as
     words, so read every description.
   - Write down the rules the reference assumes but never checks. Examples:
     list lengths that must agree, whether indices start at 0 or 1, whether a
     matrix must be symmetric, whether demand can exceed capacity. `check`
     cannot see these. An instance that breaks one can still build and solve
     while meaning something else.
4. **Find candidates, published ones first.** Start from the problem's own
   `# Source`, `# Source description` and `# Problem instances` headers. The
   repository's sources are listed in `SOURCES.md`: CSPLib problem pages, Hakan
   Kjellerstrand's model pages, the CPMpy examples, the ComplexOR repository and
   the APLAI course material. Check whether the source has further data for the
   same model. Translate faithfully: index base, units, row against column
   order, which list is which. Never change a published instance to make it
   fit. Drop it instead.
5. **Generate only when nothing published fits.** A generated instance must be
   reproducible from its note alone. Record the method, the parameters and the
   seed, for example "generated: 8 items, weights uniform 1..20, capacity half
   the total weight, Python random seed 3". Do not commit the generator. Never
   describe numbers you made up as coming from a source, even when a source
   inspired them.
6. **Design the set, not a pile.** Each candidate should vary something a wrong
   model could get wrong:
   - sizes both larger and smaller than the example;
   - a different aspect ratio (a non-square grid, more machines than jobs);
   - tight constraints, where a model missing a constraint produces a solution
     the reference rejects;
   - edge values such as zeros, a single item, or equal weights.

   A relabelling, a permutation or a uniform scaling of an existing instance
   tests almost nothing. For optimisation, avoid instances where every feasible
   solution is optimal. Aim for 3 to 5 distinct instances per problem. Go past
   5 only with a reason in the note. Small is fine: the aim is to tell models
   apart, not to be hard. Campaigns skip an instance that times out, so an
   instance the models cannot finish checks nothing.
7. **Write the candidates to a scratch file** outside the repository, as a JSON
   list. Each candidate takes the example's fields, an optional short `name`,
   and a required `note`. The note says where the instance came from (a URL,
   or "generated: ...") and what it varies. Run `check`. It refuses a candidate
   that:
   - has missing or extra fields;
   - changes a field's value types or nesting;
   - makes a field ragged or mixed-type where the example is not (a ragged
     field locks out integrations with a rectangular binder, such as
     MiniZinc);
   - has inputs identical to an instance already listed;
   - is unsatisfiable;
   - takes the reference more than 10 seconds on one OR-Tools worker, in any
     of 3 runs (for optimisation, the optimum must be proven in that time).

   A refusal means fixing the translation or dropping the candidate. Never
   loosen the gate.
8. **Append.** `check --append` appends only the candidates that passed, after
   the existing entries, and prints the IDs they got (`json:K`). Never edit,
   reorder or delete an existing entry. IDs are positions, and retained
   records cite them.
9. **Recheck the retained models** on the new IDs, without `--flag` first, and
   read the summary.
   - **All pass.** Nothing more to do.
   - **A minority fail.** Those models fitted the instances they had seen. For
     each one, read `reason` and `detail`, open the model, and confirm the
     fault is the model's. Then rerun with `--flag`.
     `generation/flags.json` then records it with the failing instance and the
     evaluator's evidence. `next_work` offers the pair again, and the site
     marks the model and stops counting it. Flagging is the policy: never
     delete or edit a retained model.
   - **`most_failed` is true.** Stop and suspect the reference or the instance
     first: recheck your translation against the rules from step 3. If the
     reference is wrong, restore the JSON file (`git checkout -- <file>`) and
     report the reference bug to the user. Never edit a reference in this
     skill. If the instance and the reference both hold up and the models share
     one misreading, flag them, and say so in the commit message.
   - **Inconclusive.** An `execution_timeout` on most models means the instance
     is too hard in practice: remove it. So does `memory_limit` on most models.
     An `infrastructure_error` means rerun. None of these is ever flagged.
10. **Run the dataset audit** (`tests.test_evaluation`). CI runs the same
    audit.
11. **Commit in batches.** Put several problems in one commit, and commit the
    dataset files together with `flags.json`. The message names the problems,
    how many instances each gained, and the models flagged. For example:
    "Add 11 instances to 4 problems; flag 2 models". Never push.

## Recording what was not added

A problem judged unable to take more instances goes under the `## Instances not
added` heading of `SOURCES.md`, one line each:

```markdown
- `sudoku`: the description fixes a 9x9 grid, so another size contradicts it.
```

`status` reads these lines and stops offering the problem. A decision a reader
would otherwise question goes under "Dataset decisions" in the same file. An
example is dropping a published instance because it is unsatisfiable.

## Rules that do not bend

- Never edit a reference, a description, the evaluator, a retained model or a
  record to make an instance fit or to clear a flag.
- Never append a candidate `check` refused. Never change the bar (10 seconds,
  3 runs) or the gate code to let one through.
- Never edit, reorder or remove an existing instance entry.
- Never flag on a timeout, an infrastructure failure or a reference error.
  Never remove a flag without a commit message saying why.
- Never invent provenance.
- Never work on a branch you did not create for this batch, and never push.

## Finish

Report, per problem:
- the instances added, with their IDs and whether each is published or
  generated;
- the candidates refused, and why;
- the recheck summary and the flags added;
- the problems recorded as not added, with the reason.

Say plainly what you did not verify, such as a rule the reference assumes
that you could not confirm from the source.
