# Standard for every generated skill

Use the [Agent Skills specification](https://agentskills.io/specification) as the
format source. Consult it when creating another skill; this summary records the
requirements used for this bundle. A skill is instructions/resources consumed
by an executing agent, not a scheduler, tool endpoint, or permission grant.

```text
skill-name/
  SKILL.md
  references/   # only when supporting detail is needed
  scripts/      # only for useful executable helpers
  assets/       # only for templates/examples actually used
```

- `SKILL.md` begins with YAML frontmatter containing `name` and `description`.
  Choose a lowercase ASCII letter/digit/hyphen name of 1–64 characters, no leading,
  trailing, or consecutive hyphens. It must equal the containing directory name.
  Description is nonempty, at most 1024 characters, and explains when to use it.
- Optional standard fields include `license`, `compatibility` (at most 500
  characters), and `metadata` (string-to-string mapping). Do not invent a license
  for third-party material or infer tool permissions from `allowed-tools`.
- Keep the entrypoint below 500 lines; put conditional detail into linked
  references. Every bundled supporting file must have a purpose and a discoverable
  link or command. Avoid placeholders and redundant manuals.
- Resource links are relative to the bundle and resolve after it is copied alone.
  Describe repository-root prerequisites explicitly; do not use `../../...` links
  to make an installable skill depend on its original source location. Bundle
  small required examples with appropriate attribution.
- Validate with `skills-ref validate <bundle>` when available, or the host's
  skill validator. Record the validator used and any gaps; do not install a
  validator silently as part of model evaluation. Check name/directory agreement,
  required fields, relative links, and the examples independently when needed.
  Format validation is not evidence that the workflow or solver works.
- Run new scripts/examples before claiming they work. Helpers should state their
  dependencies, fail clearly, preserve user data, and use actual repository APIs.
- Platform-specific discovery/install metadata is optional packaging; keep the
  canonical skill portable. Do not claim installation just because files exist
  in the source repository.

When generating another meta-skill, include its ownership, prerequisites,
outputs, bounded retries, and return conditions. Link this contract or include
the needed requirements in that new bundle so it remains self-contained. Do not
require another meta-skill to create the skill that is currently being created.
Prefer a finite procedure or reference over another agent role unless the new
role has a concrete independently testable responsibility.

## Project additions (not mandatory Agent Skills fields)

Every skill in this project carries `sources.md`: the documentation its
instructions were written from, one entry per page or version, so a reader can
check whether an API claim came from real documentation. Add an entry whenever
you add a claim that came from a specific source. Run
`generation.skills validate --project` to check format, resource links,
`sources.md` and the behavioural case schema before readiness.

Bundle bytes are not hashed here. Every attempt hashes the whole skill and
records its hash at the moment it was used, which is the record that matters for
knowing which version produced a model.

Include `evals/evals.json`: schema_version 1, skill_name, and evals entries with
id, prompt, prerequisites, expected_output, assertions and evidence_required.
Each assertion has an id and observable requirement. An eval manifest specifies
a test; an actual agent run and separate assessment provide its result.
Use `generation.behaviour` to initialize and assess runs. Never mark unexecuted
cases passed. Runtime integration tests and skill behaviour tests are distinct.
