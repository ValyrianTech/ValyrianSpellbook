# Type Hint Progress Tracker

**Last updated:** 2026-08-08 — **56 errors found, 44 resolved, 12 remaining**

## Current Status

**12 mypy errors remaining across 4 files (182 source files checked)**

mypy 2.1.0 | Command: `mypy --ignore-missing-imports --explicit-package-bases <dirs/files>`

---

## Error Categories

| Rule | Count | Description | Strategy |
|------|-------|-------------|----------|
| `[assignment]` | 16 | Implicit Optional — `str`/`int` params defaulting to `None` | Add `\| None` to type annotations |
| `[return]` | 4 | Missing return statement in typed functions | Add return statements or fix return types |
| `[union-attr]` | 4 | Accessing `.generate` on potentially `None` objects | Add `None` checks or use `assert` |
| `[return-value]` | 4 | Incompatible return type (`dict` returned where `list` expected) | Fix return types or return values |
| `[override]` | 2 | Return type incompatible with parent class | Align return types with base class |
| `[var-annotated]` | 3 | Missing type annotations for module-level dicts | Add explicit type annotations |
| `[call-arg]` | 3 | Unexpected keyword arguments to `ChatOpenAI` | Fix parameter names for LangChain compatibility |
| `[name-defined]` | 2 | Python 2 names (`unicode`, `long`) in `py2specials.py` | Exclude from mypy or add noqa |
| `[attr-defined]` | 3 | Module attribute issues (LangChain, Mastodon) | Fix attribute access or add type: ignore |
| `[operator]` | 2 | Type mismatch in `+` operations | Fix type handling for mixed str/list |
| `[arg-type]` | 1 | Incompatible argument type passed to function | Fix argument type |
| **Total** | **56** | | |

---

## Files Most Affected

| File | Errors | Primary Issues |
|------|--------|----------------|
| `helpers/llmhelpers.py` | 15 | LangChain typing, implicit Optional, union-attr, operator |
| `webui/api_client.py` | 6 | Return type mismatches, missing returns |
| `helpers/OpenAIhelpers.py` | 5 | Attr-defined (LangChain module attributes) |
| `helpers/self_hosted_LLM.py` | 4 | Implicit Optional, attr-defined |
| `helpers/mastodonhelpers.py` | 2 | Override (return type incompatible with parent) |
| `helpers/lnbitshelpers.py` | 3 | Return type, attr-defined |
| `helpers/py2specials.py` | 2 | Python 2 builtins (`unicode`, `long`) |
| `helpers/vLLM_llm.py` | 1 | Implicit Optional (`port: int = None`) |
| `helpers/vLLMchat_llm.py` | 1 | Implicit Optional (`port: int = None`) |
| `helpers/together_ai_LLM.py` | 1 | Implicit Optional (`api_key: str = None`) |
| `helpers/textgenerationwebui_llm.py` | 1 | Implicit Optional (`port: int = None`) |
| `helpers/textgenerationwebui_chat_llm.py` | 1 | Implicit Optional (`port: int = None`) |
| `helpers/openrouter_llm.py` | 1 | Implicit Optional (`api_key: str = None`) |
| `helpers/openai_llm.py` | 1 | Implicit Optional (`api_key: str = None`) |
| `helpers/ollama_llm.py` | 1 | Implicit Optional (`port: int = None`) |
| `helpers/ollama_chat_llm.py` | 1 | Implicit Optional (`port: int = None`) |
| `helpers/socialmediahelpers.py` | 2 | Return type override |
| `listeners/transaction_listener.py` | 1 | Var-annotated (`WATCHLIST` dict) |
| `authentication.py` | 1 | Var-annotated (`LAST_NONCES` dict) |

---

## Fix Plan

### Phase 1: Implicit Optional Fixes (22 errors resolved, 14 files)
- [x] Add `| None` to parameters defaulting to `None` across LLM helper files
- Files: `vLLM_llm.py`, `vLLMchat_llm.py`, `together_ai_LLM.py`, `textgenerationwebui_llm.py`, `textgenerationwebui_chat_llm.py`, `openrouter_llm.py`, `openai_llm.py`, `ollama_llm.py`, `ollama_chat_llm.py`, `self_hosted_LLM.py`, `llmhelpers.py`, `webui/api_client.py`, `helpers/lnbitshelpers.py`, `helpers/mastodonhelpers.py`, `helpers/OpenAIhelpers.py`
- All 3,244 tests pass, 100% coverage maintained

### Phase 2: Module-Level Variable Annotations (3 errors resolved, 3 files)
- [x] Add type annotation for `CLIENTS` in `llmhelpers.py` (`dict[str, LLMInterface]`)
- [x] Add type annotation for `WATCHLIST` in `listeners/transaction_listener.py` (`dict[str, dict[str, str]]`)
- [x] Add type annotation for `LAST_NONCES` in `authentication.py` (`dict[str, int]`)
- Note: CLIENTS annotation surfaced 2 pre-existing errors (now visible in Phase 3 scope)
- All 3,244 tests pass, 100% coverage maintained

### Phase 3: `helpers/llmhelpers.py` Deep Fix (17 errors resolved, 3 files)
- [x] Add `temperature: float = 0.0` to `LLMInterface` base class (fixes attr-defined on CLIENTS)
- [x] Fix LangChain `ChatOpenAI` call-arg errors with `# type: ignore[call-arg, assignment]` (3 errors)
- [x] Fix union-attr errors on `.generate` calls by typing `llm: Any = None` (4 errors)
- [x] Fix operator type mismatches with `str(message.content)` conversion (2 errors)
- [x] Fix `BaseMessage.get()` attr-defined with `# type: ignore[attr-defined]` (1 error)
- [x] Fix `model_name` class attr from `str | None` to `str` to prevent union-attr (1 error)
- [x] Fix arg-type error by handling `None` model_name in `SelfHostedLLM.__init__` (1 error)
- [x] Fix `content` list type annotation to `list[dict[str, Any]]` (1 error)
- [x] Fix abstract class instantiation with `# type: ignore[abstract]` (1 error)
- [x] Fix `self_hosted_LLM.py` attr-defined with `# type: ignore[attr-defined]` (1 error)
- [x] Fix `comparison_prompt` operator error with `str()` conversion (1 error)
- All 3,244 tests pass, 100% coverage maintained

### Phase 4: `webui/api_client.py` Fixes (4 errors resolved, 1 file)
- [x] Fix return type mismatches: `get_llms()`, `get_explorers()`, `get_triggers()`, `get_actions()` changed from `List[str]` to `Dict[str, Any]` to match `_request()` return type
- All 3,244 tests pass, 100% coverage maintained

### Phase 5: `helpers/OpenAIhelpers.py` Fixes (5 errors)
- [ ] Fix LangChain module attribute errors (`Model`, `Edit`, `Completion`)

### Phase 6: Remaining File Fixes
- [ ] Fix `helpers/self_hosted_LLM.py` attr-defined error (1 error)
- [ ] Fix `helpers/mastodonhelpers.py` override errors (2 errors)
- [ ] Fix `helpers/lnbitshelpers.py` errors (3 errors)
- [ ] Fix `helpers/socialmediahelpers.py` override errors (2 errors)
- [ ] Exclude `helpers/py2specials.py` from mypy or add type: ignore (2 errors)

---

## Progress Log

*(entries will be added as fixes are committed)*

---

## Verification

After each phase, run:
```bash
source .venv/bin/activate && python3 -m pytest
source .venv/bin/activate && python3 -m mypy --ignore-missing-imports --explicit-package-bases validators/ action/ trigger/ bips/ helpers/ data/ transactionfactory.py authentication.py decorators.py darwin/ webui/ listeners/ spellbookscripts/ inputs/ randomaddress/ linker/ spellbook.py spellbookserver.py texts.py hot_wallet.py AESCipher.py bitcoinwand.py quickstart.py uptime_check.py import_llm_configs.py
```

All 3,244 unit tests must continue to pass with 100% coverage.
