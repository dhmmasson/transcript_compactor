# Step 1 — Scaffold: `compactor/` package + pipeline skeleton + CLI

**Branch**: `feature/step1-scaffold`  
**Status**: IN PROGRESS

---

## 1. SELECTION

Feature: scaffold the `compactor/` Python package with a pass-through pipeline, a
`PipelineConfig` dataclass, and a CLI in `main.py` using argparse.

No compression logic is implemented in this step. The goal is a working skeleton
that all future phases will plug into.

---

## 2. RESEARCH

**Input data** (`transcripts/transcript1.txt`):
- Plain UTF-8 text
- Multi-paragraph, section headers (`### Section`)
- No timestamps (already stripped by the user's clipper)
- No special encoding issues

**Observations**:
- A simple pass-through pipeline is sufficient for this step
- `PipelineConfig` must hold all future flags so CLI and pipeline are decoupled
- `main()` and `parse_args()` should be separate functions so the CLI is unit-testable
  without subprocess

**Hypothesis**:
A `dataclass` for config + a single `run_pipeline(text, config) -> str` function
gives the cleanest extensibility: each future phase adds one `if config.<phase>:` block.

---

## 3. TEST CASES

All tests live in `tests/test_pipeline.py` and `tests/test_cli.py`.
Tests were written **before** any implementation (RED step).

### `tests/test_pipeline.py`

| Test | Type | Why it matters |
|---|---|---|
| `test_all_phases_disabled_by_default` | nominal | Every flag must default to False so no phase runs unintentionally |
| `test_freq_threshold_default_is_0_02` | nominal | Float default must survive field definition |
| `test_individual_flags_can_be_set_independently` | boundary | Toggling one flag must not affect others |
| `test_returns_text_unchanged_when_no_phases_enabled` | nominal | Pass-through contract: no phases → identity function |
| `test_returns_a_string` | boundary | Return type must always be `str` |
| `test_handles_empty_string` | edge case | Empty input must not raise, must return `""` |
| `test_handles_multiline_text` | edge case | Newlines and blank lines must be preserved |

### `tests/test_cli.py`

**`TestParseArgsRequired`**

| Test | Type | Why it matters |
|---|---|---|
| `test_no_arguments_exits` | edge case | `file` is required; zero args must raise `SystemExit` |

**`TestParseArgsDefaults`**

| Test | Type | Why it matters |
|---|---|---|
| `test_file_is_stored` | nominal | Positional arg stored on `args.file` as a one-element list |
| `test_blacklist_disabled_by_default` | nominal | All phase flags default to False |
| `test_frequency_disabled_by_default` | nominal | |
| `test_nlp_disabled_by_default` | nominal | |
| `test_all_disabled_by_default` | nominal | |
| `test_strip_timestamps_disabled_by_default` | nominal | `--strip-timestamps` is independent of `--all` |
| `test_stats_disabled_by_default` | nominal | |
| `test_output_is_none_by_default` | nominal | None → stdout |
| `test_freq_threshold_default_is_0_02` | nominal | Float default on CLI side |

**`TestParseArgsFlags`**

| Test | Type | Why it matters |
|---|---|---|
| `test_blacklist_flag` | nominal | Each flag individually toggles to True |
| `test_frequency_flag` | nominal | |
| `test_nlp_flag` | nominal | |
| `test_all_flag` | nominal | `--all` is parsed; expansion handled in `main()` |
| `test_strip_timestamps_flag` | nominal | |
| `test_stats_flag` | nominal | |
| `test_output_short_flag` | nominal | `-o` short form stores path |
| `test_output_long_flag` | nominal | `--output` long form stores path |
| `test_freq_threshold_custom_value` | nominal | Custom float parsed correctly |
| `test_multiple_flags_combined` | boundary | Flags are independent and composable |

**`TestParseArgsMultipleFiles`**

| Test | Type | Why it matters |
|---|---|---|
| `test_single_file_stored_as_list` | nominal | `nargs='+'` always produces a list, even for one file |
| `test_multiple_files_stored_as_list` | nominal | Multiple positional paths stored in order |
| `test_folder_path_stored_as_list` | nominal | Folder path accepted; expansion is `main()`'s responsibility |

**`TestMainBehavior`**

| Test | Type | Why it matters |
|---|---|---|
| `test_missing_file_exits_with_error` | edge case | Non-existent input must exit non-zero — no silent failure |
| `test_output_written_to_stdout` | nominal | No `-o` → result on stdout |
| `test_output_written_to_file` | nominal | `-o` flag writes result to file |
| `test_output_directory_is_created` | edge case | Missing parent dirs for `-o` are created automatically |
| `test_output_same_as_input_exits_with_error` | safety | Same in/out path must error — prevents data loss |
| `test_existing_output_file_is_overwritten` | nominal | Existing output file overwritten silently |

---

## 4. IMPLEMENTATION PLAN

### `compactor/__init__.py`
Empty file. Makes `compactor/` a package so `from compactor.pipeline import …` resolves.

### `compactor/pipeline.py`

**`PipelineConfig`** — `dataclasses.dataclass` with keyword-only defaults:

| Field | Type | Default |
|---|---|---|
| `blacklist` | `bool` | `False` |
| `frequency` | `bool` | `False` |
| `nlp` | `bool` | `False` |
| `strip_timestamps` | `bool` | `False` |
| `stats` | `bool` | `False` |
| `freq_threshold` | `float` | `0.02` |

**`run_pipeline(text: str, config: PipelineConfig) -> str`** — pass-through for now.
Returns `text` unchanged. Future phases insert here:

```python
if config.blacklist:
    text = apply_blacklist(text)
if config.frequency:
    text = apply_frequency(text, config.freq_threshold)
if config.nlp:
    text = apply_nlp(text)
return text
```

### `main.py`

**`parse_args(argv=None) -> argparse.Namespace`**:
- `file` — positional, `nargs='+'` → always a list of paths
- `--blacklist`, `--frequency`, `--nlp`, `--all`, `--strip-timestamps`, `--stats` — `store_true`
- `-o` / `--output` — `str`, default `None`
- `--freq-threshold` — `float`, default `0.02`, `dest="freq_threshold"`

**`main(argv=None)`**:
1. `args = parse_args(argv)`
2. Resolve inputs: for each path in `args.file`, expand folders to `*.txt`; error if file not found
3. If `args.all`: set blacklist + frequency + nlp to True
4. Build `PipelineConfig` from `args`
5. For each input path:
   a. Read text
   b. If output same as input → `sys.exit(1)` with message
   c. `result = run_pipeline(text, config)`
   d. Write to `args.output` (creating parent dirs) if set, else `print(result)`

---

## 5. IMPLEMENTATION NOTES

*(filled in after GREEN step)*

---

## 6. IMPROVEMENTS

*(filled in after REFACTOR step)*

---

## 7. SUMMARY

*(filled in after completion)*
