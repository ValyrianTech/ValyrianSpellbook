# Code Coverage Progress Tracker

**Last updated:** 2026-07-29

## Current Status

| Category | Lines | Status |
|----------|-------|--------|
| Measured + covered | 7,519 | 100% coverage |
| Measured, partial | 661 | `transactionfactory.py` at 25% |
| No tests, not measured | ~10,511 | Need tests + coverage config |
| **Total (excl. apps/)** | **~19,737** | |

---

## Measured Modules (in `pytest.ini` --cov)

All at 100% coverage (except `transactionfactory.py` at 25%), 2159 tests passing.

- [x] `action/` — 905 lines
- [x] `bips/` — 301 lines
- [x] `data/` — 1,432 lines (block explorers, transactions, explorer API)
- [x] `helpers/` — 3,849 lines
- [x] `trigger/` — 576 lines
- [x] `validators/` — 124 lines
- [x] `authentication.py` — 131 lines
- [x] `decorators.py` — 139 lines
- [ ] `transactionfactory.py` — 661 lines — 25% coverage, 258 lines uncovered

---

## Has Tests but NOT in Coverage Config

All previously unmeasured modules with tests have now been added to `pytest.ini` coverage config.

- [x] ~~`data/` — 2,415 lines — tests: `test_explorer.py`, `test_explorer_api.py`, `test_transaction.py`~~ → **100% coverage**
- [ ] `transactionfactory.py` — 661 lines — tests: `test_transaction_factory.py` — **25% coverage, needs more tests**
- [x] ~~`authentication.py` — 131 lines — tests: `test_authentication.py`~~ → **100% coverage**
- [x] ~~`decorators.py` — 139 lines — tests: `test_decorators.py`~~ → **100% coverage**

---

## No Tests, NOT in Coverage Config

### Packages

- [ ] `darwin/` — 1,944 lines — Genetic algorithm framework (24+ files)
- [ ] `webui/` — 1,240 lines — FastAPI web UI (routers, auth, api_client)
- [ ] `listeners/` — 439 lines — Block/transaction listeners + watchlist
- [ ] `spellbookscripts/` — 288 lines — Script execution framework (base + template)
- [ ] `inputs/` — 218 lines — Input processing
- [ ] `randomaddress/` — 171 lines — Random address selection
- [ ] `linker/` — 101 lines — Linked list implementations

### Top-level scripts

- [ ] `spellbook.py` — 1,133 lines — CLI interface
- [ ] `spellbookserver.py` — 944 lines — REST API server (Bottle)
- [ ] `texts.py` — 631 lines — Text constants/messages
- [ ] `backup_script.py` — 537 lines — GitHub→GitLab backup automation
- [ ] `import_llm_configs.py` — 240 lines — Bulk LLM config importer
- [ ] `hot_wallet.py` — 237 lines — Hot wallet management CLI
- [ ] `quickstart.py` — 148 lines — Quickstart setup script
- [ ] `uptime_check.py` — 108 lines — Uptime monitoring
- [ ] `dockerfiles/replace_placeholders.py` — 110 lines — Docker placeholder replacement
- [ ] `bitcoinwand.py` — 71 lines — Bitcoin wand utility
- [ ] `spellbookd.py` — 28 lines — Daemon launcher
- [ ] `check_domains.py` — 33 lines — Domain checker
- [ ] `AESCipher.py` — 31 lines — AES encryption
- [ ] `test_client_cloud.py` — 17 lines — Cloud test client
