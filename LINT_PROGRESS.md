# Linting Progress Tracker

**Last updated:** 2026-08-07 — **348 errors resolved, 265 remaining**

## Current Status

**265 lint errors remaining across 3 rule categories — 0 auto-fixable**

| Rule | Count | Description | Fixable? |
|------|-------|-------------|----------|
| E712 | 156 | `== False` / `== True` comparisons | Unsafe fix |
| F841 | 61 | Unused local variables | Manual |
| E402 | 48 | Module-level import not at top of file | Manual |
| **Total** | **265** | | **0 auto-fixable** |

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
- [x] **16 errors resolved across 7 small categories** (2026-08-07)
  - E701: Split multiple statements on one line in `transactionfactory.py` (1 → 0)
  - F633: Added noqa for Python 2 print syntax in `helpers/py2specials.py` (1 → 0)
  - F501: Fixed incomplete `%s: %` format strings in `integrationtests/compare_explorers.py` (2 → 0)
  - F821: Added noqa for Python 2 builtins (`unicode`, `long`) in `helpers/py2specials.py` (2 → 0)
  - F401: Added noqa for intentionally kept imports in `py3specials.py` and `test_OpenAIhelpers.py` (2 → 0)
  - E741: Renamed ambiguous variable `I` to `hmac_digest` in `bips/BIP32.py` (3 → 0)
  - F811: Removed 4 shadowed test methods in `test_mysqlhelpers.py`, merged duplicate class in `test_websockethelpers.py` (5 → 0)
- [x] **166 errors resolved: F403 + F405 star imports eliminated** (2026-08-07)
  - F403: 8 → 0, F405: 158 → 0
  - Replaced all `from helpers.py2specials import *` and `from helpers.py3specials import *` with explicit imports
  - Files changed: `bips/BIP32.py`, `data/transaction.py`, `helpers/privatekeyhelpers.py`, `helpers/publickeyhelpers.py`, `transactionfactory.py`
  - Added missing direct stdlib imports (`hashlib`, `binascii`, `re`, `sys`, `functools.reduce`) that were leaking through star imports
  - `data/transaction.py` had unused star imports removed entirely
- [x] **16 errors resolved: E721 type comparisons eliminated** (2026-08-07)
  - E721: 16 → 0
  - Replaced `type(x) == str` / `type(x) == list` with `isinstance(x, str)` / `isinstance(x, list)` in 6 LLM helper files
  - Replaced `type(x) != type(y)` with `type(x) is not type(y)` in `integrationtests/compare_explorers.py` (3 occurrences)
  - Replaced `string_types == str` with `string_types is str` in `unittests/helpers/test_py3specials.py`
  - Files changed: `helpers/llmhelpers.py`, `helpers/ollama_chat_llm.py`, `helpers/ollama_llm.py`, `helpers/self_hosted_LLM.py`, `helpers/textgenerationwebui_llm.py`, `helpers/vLLM_llm.py`, `integrationtests/compare_explorers.py`, `unittests/helpers/test_py3specials.py`

---

## Files Most Affected (by error count)

| File | Errors | Primary Issues |
|------|--------|----------------|
| `unittests/trigger/test_triggers.py` | 44 | E712 (`== False`/`== True`) |
| `unittests/action/test_twitter_actions.py` | 30 | E712 |
| `unittests/action/test_sendtransactionaction.py` | 27 | E712 |
| `spellbookserver.py` | 21 | E402, F841 |
| `unittests/helpers/test_twitterhelpers.py` | 17 | E712 |
| `unittests/helpers/test_llmhelpers.py` | 17 | E712 |
| `unittests/test_spellbookserver.py` | 12 | E712 |
| `unittests/darwin/test_fitness_function_subclasses.py` | 12 | E712 |
| `unittests/helpers/test_triggerhelpers.py` | 7 | E712 |
| `unittests/data/test_transaction.py` | 7 | E712 |
| `unittests/darwin/test_rosettastone_subclasses.py` | 7 | E712 |
| `unittests/action/test_revealsecretaction.py` | 6 | E712 |
| `unittests/action/test_commandaction.py` | 6 | E712 |
| `unittests/trigger/test_trigger.py` | 5 | E712 |
| `unittests/darwin/test_model_subclasses.py` | 5 | E712 |
| `helpers/llmhelpers.py` | 5 | E402 |
| `unittests/bips/test_mnemonic.py` | 4 | E712 |
| `unittests/action/test_spawnprocessaction.py` | 4 | E712 |
| `unittests/action/test_deletetriggeraction.py` | 4 | E712 |
| `helpers/ollama_chat_llm.py` | 2 | E402 |
| `helpers/ollama_llm.py` | 2 | E402 |
| `helpers/self_hosted_LLM.py` | 2 | E402 |
| `helpers/textgenerationwebui_llm.py` | 2 | E402 |
| `helpers/vLLM_llm.py` | 2 | E402 |
| `integrationtests/compare_explorers.py` | 3 | E712 |
| Other files (≤3 each) | 48 | Various |

---

## Category Breakdown & Strategy

### E712 — True/False Comparisons (156 errors)
**Files:** Mostly in `unittests/` (test assertions using `== False` / `== True`)

**Strategy:** Replace `assert x == False` with `assert not x` and `assert x == True` with `assert x`. Available as `--unsafe-fix` but needs careful review with mock objects.

### F841 — Unused Variables (61 errors)
**Files:** `webui/routers/`, `unittests/`, `spellbookserver.py`, various

**Strategy:** Remove assignments to unused variables or prefix with `_`. Many are `result = ...` where only the side effect matters.

### E402 — Import Not At Top (48 errors)
**Files:** `spellbookserver.py`, `helpers/llmhelpers.py`, `helpers/ollama_*.py`, `helpers/self_hosted_LLM.py`, `helpers/vLLM_llm.py`, `helpers/textgenerationwebui_llm.py`, `darwin/darwin.py`, various

**Strategy:** Caused by `sys.path` manipulation before imports. Can be fixed by reorganizing or adding `# noqa: E402` where the pattern is intentional.

## Bug Fixes During Linting Work

- **`helpers/mailhelpers.py`** — Ruff auto-fix replaced Python 2/3 compat try/except with `pass`, preventing `encoders` from being imported. Fixed by replacing with direct `from email import encoders`.
- **`helpers/py3specials.py`** — Ruff auto-fix removed `from functools import reduce` as "unused", but it was needed by `transactionfactory.py` via `import *`. Restored manually.
- **`unittests/helpers/test_OpenAIhelpers.py`** — Ruff auto-fix removed `import helpers.OpenAIhelpers` as "unused", but the import side-effect was required for the test. Restored manually.

---

## Summary

The Valyrian Spellbook repository had **613 lint errors** initially. Ruff's `--fix` resolved 150 auto-fixable issues. Two regressions from the auto-fix were identified and corrected. An additional 16 errors across 7 small categories were manually resolved. All 166 F403/F405 star import errors were eliminated by replacing `import *` with explicit imports. All 16 E721 type comparison errors were resolved by replacing `type() ==` with `isinstance()` and `type() != type()` with `type() is not type()`. **265 errors remain**, primarily true/false comparisons (E712) and unused variables (F841). All 3,244 unit tests continue to pass with 100% coverage.
