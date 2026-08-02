# Code Coverage Progress Tracker

**Last updated:** 2026-08-02 (updated again)

## Current Status

| Category | Lines | Status |
|----------|-------|--------|
| Measured + covered | 10,188 | 100% coverage |
| Measured, partial | 661 | `transactionfactory.py` at 99% |
| Darwin (now measured) | 8,936 | 99% coverage (130 lines uncovered) |
| spellbookscripts (now measured) | 188 | 100% coverage |
| `spellbook.py` (now measured) | 608 | 100% coverage |
| `spellbookserver.py` (now measured) | 678 | 100% coverage |
| No tests, not measured | ~6,873 | Need tests + coverage config |
| **Total (excl. apps/)** | **~28,458** | **99% measured coverage** |

---

## Measured Modules (in `pytest.ini` --cov)

All at 100% coverage (except `transactionfactory.py` at 99% and `darwin/` at 99%), 3139 tests passing.

- [x] `action/` — 905 lines
- [x] `bips/` — 301 lines
- [x] `darwin/` — 8,936 lines — 99% coverage (130 lines uncovered: `darwin.py` main entry, `evolver.py` `start()` method, `population.py` unknown encoding raise)
- [x] `data/` — 1,432 lines (block explorers, transactions, explorer API)
- [x] `helpers/` — 3,849 lines
- [x] `trigger/` — 576 lines
- [x] `validators/` — 124 lines
- [x] `authentication.py` — 131 lines
- [x] `decorators.py` — 139 lines
- [x] `transactionfactory.py` — 661 lines — 99% coverage, 3 lines uncovered (bugs in `add_op_return` and `sign` with bytes/dict inputs)
- [x] `webui/` — 1,240 lines — 100% coverage (commit `8ba37cf`)
- [x] `listeners/` — 133 lines — 100% coverage
- [x] `spellbookscripts/` — 188 lines — 100% coverage
- [x] `inputs/` — 218 lines — 100% coverage
- [x] `randomaddress/` — 172 lines — 100% coverage
- [x] `linker/` — 101 lines — 100% coverage
- [x] `spellbook.py` — 608 lines — 100% coverage
- [x] `spellbookserver.py` — 678 lines — 100% coverage (extracted `main()` function, added `TestSpellbookInit` for `__init__` paths, `# pragma: no cover` on `__main__` guard)

---

## Has Tests but NOT in Coverage Config

All previously unmeasured modules with tests have now been added to `pytest.ini` coverage config.

- [x] ~~`data/` — 2,415 lines — tests: `test_explorer.py`, `test_explorer_api.py`, `test_transaction.py`~~ → **100% coverage**
- [x] ~~`transactionfactory.py` — 661 lines — tests: `test_transaction_factory.py`~~ → **99% coverage**
- [x] ~~`authentication.py` — 131 lines — tests: `test_authentication.py`~~ → **100% coverage**
- [x] ~~`decorators.py` — 139 lines — tests: `test_decorators.py`~~ → **100% coverage**

---

## No Tests, NOT in Coverage Config

### Packages

- [x] ~~`darwin/` — 8,936 lines — Genetic algorithm framework (24+ files)~~ → **99% coverage** (commit `5d108b3`)
- [x] ~~`webui/` — 1,240 lines — FastAPI web UI (routers, auth, api_client)~~ → **100% coverage** (commit `8ba37cf`)
- [x] ~~`listeners/` — 439 lines — Block/transaction listeners + watchlist~~ → **100% coverage**
- [x] ~~`spellbookscripts/` — 288 lines — Script execution framework (base + template)~~ → **100% coverage**
- [x] ~~`inputs/` — 218 lines — Input processing~~ → **100% coverage**
- [x] ~~`randomaddress/` — 172 lines — Random address selection~~ → **100% coverage**
- [x] ~~`linker/` — 101 lines — Linked list implementations~~ → **100% coverage**

### Top-level scripts

- [x] ~~`spellbook.py` — 608 lines — CLI interface~~ → **100% coverage** (104 tests; fixed missing `get_hivemind` argparse subparser)
- [x] ~~`spellbookserver.py` — 944 lines — REST API server (Bottle)~~ → **100% coverage** (101 tests; fixed `get_llm_config` NoneType bug; extracted `main()` function; added `TestSpellbookInit` for `__init__` runtime paths)
- [x] `texts.py` — 631 lines — Text constants/messages — **100% coverage**
- [ ] `backup_script.py` — 537 lines — GitHub→GitLab backup automation
- [x] `import_llm_configs.py` — 240 lines — Bulk LLM config importer — **100% coverage** (46 tests)
- [ ] `hot_wallet.py` — 237 lines — Hot wallet management CLI
- [ ] `quickstart.py` — 148 lines — Quickstart setup script
- [ ] `uptime_check.py` — 108 lines — Uptime monitoring
- [ ] `dockerfiles/replace_placeholders.py` — 110 lines — Docker placeholder replacement
- [ ] `bitcoinwand.py` — 71 lines — Bitcoin wand utility
- [ ] `spellbookd.py` — 28 lines — Daemon launcher
- [ ] `check_domains.py` — 33 lines — Domain checker
- [ ] `AESCipher.py` — 31 lines — AES encryption
- [ ] `test_client_cloud.py` — 17 lines — Cloud test client
