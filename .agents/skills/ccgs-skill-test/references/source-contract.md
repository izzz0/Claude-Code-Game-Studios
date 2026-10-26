# Skill Test Contract

This contract tests installed Codex studio skills and native role definitions. It is read-only by default. It may modify a skill only when explicitly authorized within the accepted brief.

## Scope and resolution

Resolve the repository root, then read `studio-tests/catalog.yaml`. The catalog maps skills to specs under `studio-tests/skills/**` and native roles to specs under `studio-tests/agents/**`. Resolve implementations from `.agents/skills/ccgs-[name]/SKILL.md` and roles from the `.codex/agents/ccgs-*.toml` inventory. Do not assume a skill is automatically preloaded into a role context. Read the skill and every required file under its `references/` directory.

Keep catalog expected sets and filesystem discovered sets separate. Report missing catalog entries, missing specs, and extra resources instead of silently dropping them.
The migrated catalog and spec corpus is authoritative expected data: preserve every source case, dependency, output path, normal flow, boundary, and recovery flow. Codex-native path/role substitutions are allowed only where they preserve that business meaning.

## Four modes

### `static [name|all]`

Parse without executing. A skill requires only valid frontmatter with exactly `name` and `description`; `name` matches its directory and `description` is a non-empty YAML scalar. Do not require argument hints, user-invocable flags, tool-permission metadata, phase counts, fixed models, or minimum length. Check that referenced local paths exist and declared routes resolve to installed `ccgs-*` skills or configured native roles. Static output is structural, never a behavior PASS.

For roles, parse TOML with the runtime TOML parser (`tomllib` on Python 3.11+ or the repository-compatible equivalent). Require the role identity and fields required by its native contract; do not infer model or tool permissions from absent fields and do not require overrides.

### `spec [name]`

Resolve the catalog entry, read the complete expected spec and implementation inputs, and evaluate assertions as `PASS`, `FAIL`, `PARTIAL`, or `NOT ASSESSED`. This is a static contract evaluation, not execution of the skill, game, helper, or role. A required native role that cannot be dispatched or returns no evidence is `NOT ASSESSED`, never fabricated as PASS. Preserve every source case's normal, boundary, dependency, and recovery expectation; wording checks cannot substitute for behavior evidence.

Cases may describe native user interaction, but implementation uses the current host interaction mechanism and automation-mode rules. Ordinary authorized edits are scoped to the accepted brief; no case requires approval for every individual file. Read-only reviews do not write code, stories, QA artifacts, receipts, or checkpoints.

### `category [name|all]`

Read the matching section of `studio-tests/quality-rubric.md` and evaluate independent native cases against it. Do not call an external model API, pin a model, or treat a role file as execution evidence. Missing native role output, fixture input, or runner is `NOT ASSESSED`. Category output is a report and does not mutate the catalog.

### `audit`

Enumerate catalogued and discovered skills and native roles. Report each spec path, implementation path, category, and last recorded result without inventing a verdict. Separate expected coverage from observed execution and trust evidence. Audit is read-only and does not update catalog fields.

## Verdict and evidence rules

Use `FAIL` for a contradicted contract or observed failure; `NOT ASSESSED` for missing/unreadable inputs, unavailable dispatch, absent runner, zero results, or unobserved execution; `PARTIAL` only when partially evidenced; and `PASS` only when the written contract and required evidence are established. A valid file or receipt alone is not a quality verdict. Keep expected specs, static observations, and actual execution results separate.

If improvement is explicitly authorized, preserve source cases, make the smallest scoped change, then run static/spec/category checks again and report before/after evidence. Never grade from instruction wording or a constant PASS: skill-improve retains test -> fix -> retest and real grade data.
