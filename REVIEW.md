# Review instructions

Read by `/codex:review`, `/code-review`, and human reviewers alike.

## Passes

Run these passes and tag every finding with its pass:

- **Bugs**: logic errors, broken edge cases, regressions in tokenization, tagging, or scoring.
- **Security**: unsafe deserialization, `eval`-like execution, shell calls built from input, and
  file reads that escape the package data directory. Ruff's bandit (`S`) rules cover the obvious
  cases, so look for what they cannot see.
- **Compliance**: the change matches the issue spec and the approved plan, and respects the focus
  areas below.

## Repo focus

- **Tagger and tokenizer behavior is the public contract**: any change to how a term is segmented,
  tagged, or classified as a single noun is user-visible and needs a test that pins the new output.
  Silent default changes are Important, not nits.
- **Sentiment resources are data**: changes under `src/ekonlpy/data/` and the sentiment dictionaries
  need a stated provenance in the PR, because scores shift for every downstream user.
- **Public API**: added, renamed, or re-signatured public functions need a docs update and a
  CHANGELOG-worthy commit message; the package ships `py.typed`, so signature changes are typed
  API changes.
- **Python floor**: shipped code must run on 3.9 even though development pins 3.12.
- **Dependencies**: a new runtime dependency belongs in `pyproject.toml`, declared where `deptry`
  can see it. The lock file is gitignored, so it never appears in a diff; what a reviewer can check
  is that the declaration matches the imports and that the author ran `make check`.

## What Important means here

Reserve Important for findings that change tagging or sentiment output without a test, break the
3.9 floor, alter a public signature without documentation, or introduce an unvetted dependency.
Style and naming are nits.

## Cap the nits

Report at most 5 nits per review; summarize the rest as a count.

## Do not report

- `src/ekonlpy/_version.py`, which semantic-release generates.
- Findings the gates already catch: the `uv lock --locked` consistency check, the configured
  pre-commit hooks (pygrep checks, Python whitespace and end-of-file fixers, YAML/JSON/large-file
  checks), `deptry`, and pytest.
- Commit-message format, which the commitizen `commit-msg` hook rejects before a commit exists.

**Not on that list**: ruff, black, isort, flake8, and mypy are configured in `pyproject.toml` but no
gate invokes them, and coverage has no failure threshold. Findings those tools would catch,
including type errors and lint violations, stay in scope for review.

## Feedback into CLAUDE.md

When the same finding appears twice, the correction goes into `CLAUDE.md` in the same PR.

---

Findings do not approve or block on their own. Human approval and the merge-on-instruction gate
stay as they are (`_meta/rules/development-lifecycle.md` §2, §6). CI runs on every PR and on
pushes changing source, tests, dependencies, Makefile, Python pin, hooks, or the test workflow.
Review the actual Python/OS matrix and installed-artifact results alongside local verification.
