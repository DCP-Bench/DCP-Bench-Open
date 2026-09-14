# Operations and skill improvement

Use the repository's `generation.manage` and `generation.skills` commands;
read repository `generation/AGENTS.md` for exact syntax and schemas. They are
shared executable helpers, not another agent layer. Run from the repository root
using its Python environment. Preserve complete stdout/stderr for every build,
test and failed setup attempt in `generation/runs/RUN/setup/SOLVER/ATTEMPT/`.
Create setup attempts with `generation.manage setup-attempt --run RUN --solver
SOLVER --skill SETUP_SKILL_PATH`. It freezes the complete bundle and records
the agent from run configuration. Use its returned path. Record setup_finished,
setup_blocked or interrupted with `generation.manage event`; include evidence
paths. Set the actual agent in run config; unknown is recorded if unavailable.

Freeze the entire setup skill at the start of each attempt; skill edits do not
change instructions already used. A diagnosed setup mistake may suggest a runner
repair, a solver instruction correction, or a setup procedure improvement. Apply
code repairs with integration regressions; propose instruction changes only when
there is a supported general lesson. Do not treat every failure as a skill bug.

All skill levels use the same workflow:
1. Record observed failure, cause evidence, affected skill, and reproducer.
2. Copy the canonical bundle to a working candidate with the same directory name.
3. Add a behavioural regression scenario; keep its independent acceptance checks
   outside the candidate bundle's editable instructions.
4. Run `generation.skills validate --project` on the candidate to verify its
   format, resource links, `sources.md` and eval schema.
5. Use `generation.skills propose`, then `check` with coordinator-owned trusted
   commands targeting `{skill}`. Both old and candidate versions are tested.
6. Apply only a validated unchanged proposal using `generation.skills apply`.
   Rejected or untested proposals remain pending with evidence. Meta/setup-skill
   changes take effect on the next attempt/run, never retroactively.

A command passing means that check passed, not that a general improvement was
proved. Behavioural scenarios need an executing agent plus evidence assessment;
format validators cannot substitute for them. The helpers automatically log
`skill_proposed`, `skill_checked` (validated/rejected), and `skill_applied`
under the same run ID. Use an explicit event for pending/deferred decisions.
No new agent is needed just to follow this update procedure.

New modelling skills must record their documentation in `sources.md` and include
behavioural scenarios.
Use [the skill standard](skill-standard.md) and this bundle's `evals/evals.json`
as a schema example. Run cases through a capable agent and store observed results
outside the installed skill bundle. Do not write 'passed' merely from reading a
scenario. Consult `generation/AGENTS.md` for the evaluation evidence format.
