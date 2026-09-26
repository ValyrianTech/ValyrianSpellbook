# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Renamed 37 files to follow PEP 8 snake_case naming conventions. Notable source module renames:
  - `bips/BIP32.py` -> `bips/bip32.py`
  - `bips/BIP39.py` -> `bips/bip39.py`
  - `bips/BIP44.py` -> `bips/bip44.py`
  - `helpers/BIP44.py` -> `helpers/bip44.py`
  - `helpers/OpenAIhelpers.py` -> `helpers/openaihelpers.py`
  - `helpers/self_hosted_LLM.py` -> `helpers/self_hosted_llm.py`
  - `helpers/together_ai_LLM.py` -> `helpers/together_ai_llm.py`
  - `helpers/vLLM_llm.py` -> `helpers/vllm_llm.py`
  - `helpers/vLLMchat_llm.py` -> `helpers/vllmchat_llm.py`
  - The remaining renames are integration-test and unit-test files renamed to snake_case.

### Fixed

- Resolved all remaining ruff lint errors; the repository is now lint-clean.
- Resolved all remaining mypy type-check errors; the repository is now type-check clean.

### Internal

- Applied 1,575 ruff safe auto-fixes across the codebase.
- Added type annotations and fixed mypy errors across the codebase.
- Removed dead code with vulture and added a `vulture_whitelist.py` file to whitelist framework hooks, dynamic-plugin APIs, and injected pytest fixtures. Deleted the top-level `__init__.py`.
- Made unit tests self-contained and runnable in a fresh clone, and expanded test coverage.
- Added `.SWE/` to `.gitignore` for SWE pipeline artifacts.
