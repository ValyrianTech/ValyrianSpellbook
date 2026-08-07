# Linting Progress Tracker

**Last updated:** 2026-08-07 — **150 auto-fixable errors resolved, 463 remaining**

## Current Status

**463 lint errors remaining across 12 rule categories — 2 auto-fixable**

| Rule | Count | Description | Fixable? |
|------|-------|-------------|----------|
| F405 | 158 | `import *` with undefined names used | Manual (needs explicit imports) |
| E712 | 156 | `== False` / `== True` comparisons | Unsafe fix |
| F841 | 61 | Unused local variables | Manual |
| E402 | 48 | Module-level import not at top of file | Manual |
| E721 | 16 | `type() ==` comparisons | Manual |
| F403 | 8 | `from module import *` | Manual |
| F811 | 5 | Redefined while unused | Manual |
| E741 | 3 | Ambiguous variable names (`l`, `I`, `O`) | Manual |
| F401 | 2 | Unused imports | Auto-fixable |
| F501 | 2 | Invalid percent-format string | Manual |
| F821 | 2 | Undefined names | Manual |
| E701 | 1 | Multiple statements on one line | Manual |
| F633 | 1 | Invalid print syntax | Manual |
| **Total** | **463** | | **2 auto-fixable** |

---

## Progress Made

### Completed

- [x] **150 auto-fixable errors resolved** (2026-08-07, commit `4d7e6a6`)
  - F401: Unused imports removed (128 → 2)
  - F841: Unused variables removed (64 → 61)
  - F541: f-string missing placeholders fixed (9 → 0)
  - F632: `is` used with literals fixed (4 → 0)
  - F522: String format extra named arguments fixed (1 → 0)
  - E401: Multiple imports on one line fixed (1 → 0)
  - F811: Redefined while unused fixed (10 → 5)
- [x] **Fixed broken `encoders` import in `mailhelpers.py`** (2026-08-07, commit `35337c7`)
  - Ruff auto-fix broke Python 2/3 compat try/except pattern, replaced with direct Python 3 import
- [x] **Fixed broken `reduce` import in `py3specials.py`** (2026-08-07, commit `4d7e6a6`)
  - Restored `from functools import reduce` needed by `transactionfactory.py` via `import *`
- [x] **Restored side-effect import in `test_OpenAIhelpers.py`** (2026-08-07, commit `4d7e6a6`)
  - Ruff removed `import helpers.OpenAIhelpers` that was needed for module initialization test

---

## Files Most Affected (by error count)

| File | Errors | Primary Issues |
|------|--------|----------------|
| `transactionfactory.py` | 97 | F405 (star import from py3specials), E712 |
| `unittests/trigger/test_triggers.py` | 44 | E712 (`== False`/`== True`) |
| `unittests/action/test_twitter_actions.py` | 30 | E712 |
| `helpers/publickeyhelpers.py` | 30 | F405, E721 |
| `unittests/action/test_sendtransactionaction.py` | 27 | E712 |
| `bips/BIP32.py` | 24 | F405, E402 |
| `spellbookserver.py` | 21 | F405, E402 |
| `unittests/helpers/test_twitterhelpers.py` | 17 | E712 |
| `unittests/helpers/test_llmhelpers.py` | 17 | E712 |
| `helpers/privatekeyhelpers.py` | 17 | F405, E721 |
| `unittests/test_spellbookserver.py` | 12 | E712 |
| `unittests/darwin/test_fitness_function_subclasses.py` | 12 | E712 |
| `unittests/helpers/test_triggerhelpers.py` | 7 | E712 |
| `unittests/data/test_transaction.py` | 7 | E712 |
| `unittests/darwin/test_rosettastone_subclasses.py` | 7 | E712 |
| `unittests/action/test_revealsecretaction.py` | 6 | E712 |
| `unittests/action/test_commandaction.py` | 6 | E712 |
| `unittests/trigger/test_trigger.py` | 5 | E712 |
| `unittests/helpers/test_mysqlhelpers.py` | 5 | E712 |
| `unittests/darwin/test_model_subclasses.py` | 5 | E712 |
| `integrationtests/compare_explorers.py` | 5 | E712 |
| Other files (≤4 each) | 96 | Various |

---

## Category Breakdown & Strategy

### F405 + F403 — Star Imports (166 errors)
**Files:** `transactionfactory.py`, `helpers/publickeyhelpers.py`, `helpers/privatekeyhelpers.py`, `bips/BIP32.py`, `spellbookserver.py`, `helpers/py2specials.py`

**Strategy:** Replace `from module import *` with explicit imports of only the names actually used. This is the largest category but concentrated in a few files.

### E712 — True/False Comparisons (156 errors)
**Files:** Mostly in `unittests/` (test assertions using `== False` / `== True`)

**Strategy:** Replace `assert x == False` with `assert not x` and `assert x == True` with `assert x`. Available as `--unsafe-fix` but needs careful review with mock objects.

### F841 — Unused Variables (61 errors)
**Files:** `webui/routers/`, `unittests/`, various

**Strategy:** Remove assignments to unused variables or prefix with `_`. Many are `result = ...` where only the side effect matters.

### E402 — Import Not At Top (48 errors)
**Files:** `transactionfactory.py`, `bips/BIP32.py`, `spellbookserver.py`, various

**Strategy:** Caused by `sys.path` manipulation before imports. Can be fixed by reorganizing or adding `# noqa: E402` where the pattern is intentional.

### E721 — Type Comparisons (16 errors)
**Files:** `helpers/publickeyhelpers.py`, `helpers/privatekeyhelpers.py`

**Strategy:** Replace `type(x) == bytes` with `isinstance(x, bytes)`.

---

## Bug Fixes During Linting Work

- **`helpers/mailhelpers.py`** — Ruff auto-fix replaced Python 2/3 compat try/except with `pass`, preventing `encoders` from being imported. Fixed by replacing with direct `from email import encoders`.
- **`helpers/py3specials.py`** — Ruff auto-fix removed `from functools import reduce` as "unused", but it was needed by `transactionfactory.py` via `import *`. Restored manually.
- **`unittests/helpers/test_OpenAIhelpers.py`** — Ruff auto-fix removed `import helpers.OpenAIhelpers` as "unused", but the import side-effect was required for the test. Restored manually.

---

## Summary

The Valyrian Spellbook repository had **613 lint errors** initially. Ruff's `--fix` resolved 150 auto-fixable issues. Two regressions from the auto-fix were identified and corrected. **463 errors remain**, primarily star imports (F405/F403) and true/false comparisons (E712), concentrated in a small number of files. All 3,243 unit tests continue to pass with 100% coverage.
