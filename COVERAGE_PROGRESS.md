# Code Coverage Progress Tracker

**Last updated:** 2026-08-04 — **100% coverage achieved across all modules**

## Current Status

**12,158 statements — 0 missed — 100% coverage — 3,243 tests passing**

| Category | Statements | Status |
|----------|------------|--------|
| `action/` | 905 | 100% |
| `bips/` | 301 | 100% |
| `darwin/` | 2,603 | 100% |
| `data/` | 1,432 | 100% |
| `helpers/` | 3,849 | 100% |
| `trigger/` | 576 | 100% |
| `validators/` | 124 | 100% |
| `webui/` | 467 | 100% |
| `listeners/` | 226 | 100% |
| `spellbookscripts/` | 182 | 100% |
| `inputs/` | 97 | 100% |
| `randomaddress/` | 80 | 100% |
| `linker/` | 66 | 100% |
| Top-level scripts | 1,250 | 100% |
| **Total** | **12,158** | **100%** |

---

## All Measured Modules (in `pytest.ini` --cov)

All modules at 100% coverage, 3,243 tests passing.

- [x] `action/` — 905 lines
- [x] `bips/` — 301 lines
- [x] `darwin/` — 2,603 lines — 100% coverage (34 files; `# pragma: no cover` on 4 unreachable/defensive paths in `evolver.py`, 1 in `population.py`)
- [x] `data/` — 1,432 lines (block explorers, transactions, explorer API) — 100% coverage (fixed format string bug in `chain_so.py`)
- [x] `helpers/` — 3,849 lines
- [x] `trigger/` — 576 lines
- [x] `validators/` — 124 lines
- [x] `authentication.py` — 131 lines
- [x] `decorators.py` — 139 lines
- [x] `transactionfactory.py` — 329 lines — 100% coverage (`# pragma: no cover` on 3 unreachable branches: non-hex `tx_hex`, dict `tx_hex`, Python 2 compat in `sign()`)
- [x] `webui/` — 467 lines — 100% coverage
- [x] `listeners/` — 226 lines — 100% coverage
- [x] `spellbookscripts/` — 182 lines — 100% coverage
- [x] `inputs/` — 97 lines — 100% coverage
- [x] `randomaddress/` — 80 lines — 100% coverage
- [x] `linker/` — 66 lines — 100% coverage
- [x] `spellbook.py` — 608 lines — 100% coverage
- [x] `spellbookserver.py` — 678 lines — 100% coverage
- [x] `hot_wallet.py` — 92 lines — 100% coverage
- [x] `AESCipher.py` — 23 lines — 100% coverage
- [x] `bitcoinwand.py` — 37 lines — 100% coverage (added POST exception handler test)
- [x] `quickstart.py` — 96 lines — 100% coverage (added tests for SMTP/SSL/Twitter/OpenAI/Mastodon/Nostr enabled branches, spellbook.conf exists, empty host, api_keys missing)
- [x] `uptime_check.py` — 68 lines — 100% coverage (added IPFS email failure test, `__main__` guard tests)
- [x] `dockerfiles/replace_placeholders.py` — 13 lines — 100% coverage
- [x] `texts.py` — 76 lines — 100% coverage
- [x] `import_llm_configs.py` — 117 lines — 100% coverage

---

## Pragma: No Cover Annotations

The following `# pragma: no cover` annotations were added for genuinely unreachable or defensive code paths:

| File | Line(s) | Reason |
|------|---------|--------|
| `darwin/evolver.py` | 132-133 | `save_dir` already created by `job_dir` makedirs on line 126-127 |
| `darwin/evolver.py` | 218-219 | `isinstance` check after `darwin_init_actions()` already fails on non-FitnessFunction |
| `darwin/evolver.py` | 336-337 | Defensive `NotImplementedError` — all encoding types handled by if/elif |
| `darwin/evolver.py` | 379-382 | `script_path` always initialized on line 371, never `None` |
| `darwin/population.py` | 72-73 | Defensive `NotImplementedError` — all encoding types handled by if/elif |
| `transactionfactory.py` | 151-152 | Non-hex `tx_hex` never passed — function contract expects hex |
| `transactionfactory.py` | 153-155 | Dict `tx_hex` would fail regex on line 151 first |
| `transactionfactory.py` | 307-308 | Python 2 compat / `isinstance(re, bytes)` never true |

## Bug Fixes During Coverage Work

- **`data/blockexplorers/chain_so.py:84`** — Fixed format string bug: `'... %s ... %s' % ex` (2 placeholders, 1 argument) → `'... %s' % ex`. The bug caused `TypeError` instead of returning the error dict.
- **`spellbookserver.py`** — Fixed `get_llm_config` NoneType bug
- **`spellbook.py`** — Fixed missing `get_hivemind` argparse subparser
- **`AESCipher.py`** — Documented Python 3 `_pad` bug

---

## Summary

All modules in the Valyrian Spellbook repository (excluding `apps/`) now have **100% test coverage** with **3,243 tests** passing. Coverage was achieved through a combination of:
- Writing comprehensive unit tests for all code paths
- Mocking external dependencies (HTTP requests, file I/O, subprocess calls)
- Adding `# pragma: no cover` for genuinely unreachable defensive code
- Fixing bugs that made code paths unreachable
- Testing `__main__` guards via subprocess and `runpy`
