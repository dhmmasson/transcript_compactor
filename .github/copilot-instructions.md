# Copilot Instructions for transcript_compactor

- Project: transcript_compactor
- Version: 0.0.1
- Dependency management: uv (https://github.com/astral-sh/uv)
- License: MIT
- Plan: see `plan.md`

## Checklist
- [x] Scaffolded Python project with pyproject.toml
- [x] Added README.md
- [x] Added MIT LICENSE
- [x] Wrote plan.md
- [x] Step 1: Scaffold compactor/ package + pipeline skeleton + CLI
- [x] Step 2: Phase 1 — blacklist filter
- [ ] Step 3: Phase 2 — frequency analysis
- [ ] Step 4: Phase 3 — NLP filter (spacy)
- [ ] Step 5: Packaging (hatchling, console script, uv build)

---

## Development Process

All feature work follows this strict cycle. Never skip steps or reorder them.

### 1. SELECTION
Pick one feature from the plan. One feature per cycle. A cycle is many commits. Reference it explicitly. Create a documentation file. Example: `docs/phase1_blacklist.md` for "Phase 1 — blacklist filter". This file will contain the research, test cases, implementation plan, and summary for this feature. Create a branch named after the feature: `feature/phase1-blacklist`. This will help keep work organized and reviewable.

### 2. RESEARCH
- Read the relevant transcript data
- Run small experiments (tokenization, regex, frequency) to validate assumptions
- Write your hypothesis about the data or implementation: what will the implementation do and why.
- Ask clarifying questions before writing any code. 

### 3. TEST-WRITING (RED)
- Write _failing_ tests **before any implementation**
- Tests must fail because the function/module does not exist yet
- Use AAA pattern: Arrange – Act – Assert
- Cover: nominal case, edge cases, boundary conditions
- Document each test case: what it tests and why it matters
- Run tests to confirm they are **red**
- **Stop here** and output a commit message for review:
  `test(<scope>): add failing tests for <feature>`

### 4. DOCUMENTATION + IMPLEMENTATION PLAN
- Describe precisely how the implementation will work: algorithm, data structures, edge case handling
- Update `plan.md` if the design deviates from the original
- **Commit** before writing implementation:
  `docs(<scope>): document implementation approach for <feature>`

### 5. IMPLEMENT (GREEN)
- Write the **minimum** code to make the failing tests pass
- Do not add untested behaviour
- If the implementation diverges from the plan, update the plan first, then implement
- Run the test suite: all tests must be **green**
- **Commit**:
  `feat(<scope>): implement <feature>`

### 6. IMPROVE (REFACTOR)
- Check coverage: are there untested paths?
- Remove dead code
- Improve readability without changing behaviour
- Re-run tests: still **green**
- **Commit** if changes are non-trivial:
  `refactor(<scope>): clean up <feature>`

### 7. SUMMARIZE
- Add inline comments where intent is non-obvious
- Update `plan.md` checklist: mark completed step
- Update `.github/copilot-instructions.md` checklist above
- Note what could be improved in a future cycle

---

## TDD Rules (non-negotiable)

- **Never** write implementation before the failing test exists
- **Never** combine RED and GREEN in a single step
- **Never** prompt "write tests and implementation together"
- One feature per TDD cycle
- Tests describe behaviour, not implementation: `test_removes_filler_words_from_sentence`, not `test_blacklist_function`
- Test names: `test_<what>_<condition>_<expected>` when helpful

---

## Commit Convention

Format: `<type>(<scope>): <description>`

fix: A bug fix. Correlates with PATCH in SemVer
feat: A new feature. Correlates with MINOR in SemVer
docs: Documentation only changes
style: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
refactor: A code change that neither fixes a bug nor adds a feature
perf: A code change that improves performance
test: Adding missing or correcting existing tests
build: Changes that affect the build system or external dependencies (example scopes: pip, docker, npm)
ci: Changes to CI configuration files and scripts (example scopes: GitLabCI)

| Type | When |
|---|---|
| `test` | Adding failing tests (RED step) |
| `docs` | Implementation plan / inline docs |
| `feat` | Implementation (GREEN step) |
| `refactor` | Cleanup (IMPROVE step) |
| `chore` | Tooling, config, packaging |

Commits are **atomic**: one logical change per commit. Stop and output the commit message for user review before moving to the next step.

---

## Running the Project

```sh
# Development
uv run main.py transcripts/transcript1.txt --blacklist --stats
uv run main.py transcripts/transcript1.txt --all -o out.txt

# Tests
uv run pytest

# After packaging
uv tool install .
transcript-compactor transcripts/transcript1.txt --all
```

---

## Dependencies

- Phases 1 and 2: stdlib only, no new deps
- Phase 3: `uv add spacy` (added only when Phase 3 is implemented)
- Packaging: hatchling (build backend)

## Current Phase 1 Contract

- Phase 1 is exact-match blacklist removal only.
- No filler-word heuristics, sponsor detection, or regex-based sentence filtering are part of this cycle.
- Default fallback blacklist is conservative: `the`, `a`, `an`, `this`, `that`, `those`, `these`.
- Punctuation is preserved unless blacklist removals create adjacent punctuation, in which case the highest-priority mark survives: `,` < `;` < `.` < `!` < `?`.
