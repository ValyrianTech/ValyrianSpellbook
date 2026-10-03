# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Breaking

- `RunCommandProcess` (`helpers/runcommandprocess.py`) no longer runs commands through a shell (previously `Popen(..., shell=True)`, now `shlex.split` + `Popen(..., shell=False)`). As a result, shell features are no longer supported for string commands: pipes (`|`), redirection (`>`, `>>`, `<`), command chaining (`&&`, `||`, `;`), `$VAR`/`${VAR}` environment-variable expansion, command substitution (backticks / `$(...)`), glob expansion (`*`, `?`, `[...]`), subshells (`(...)`) and brace expansion (`{...}`).
  - Metacharacters are now passed as literal arguments (previously they silently misbehaved).
  - `RunCommandProcess` logs a `WARNING` by default when a string command contains shell metacharacters, and raises a `ValueError` when constructed with `strict=True`.
  - To keep shell features, invoke a shell explicitly by passing an argv list such as `['sh', '-c', '...']` or `['bash', '-lc', '...']`, or refactor the command to avoid shell features.

### Changed

- Relicensed the project from the GNU General Public License v3 (GPL-3.0) to the MIT License. The top-level `LICENSE` file now contains the standard MIT License text (Copyright (c) 2026 ValyrianTech), the README has a new `License` section, and `pyproject.toml` declares the MIT license (`name = "valyrian-spellbook"`).
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
- `AESCipher.encrypt()` now requires `bytes` input (raising `TypeError` otherwise) and returns base64-encoded `bytes`, and `AESCipher.decrypt()` now raises `ValueError` on tampered, malformed, or corrupt input.

### Fixed

- Resolved all remaining ruff lint errors; the repository is now lint-clean.
- Resolved all remaining mypy type-check errors; the repository is now type-check clean.
- Nonces are no longer lost on server restart, and concurrent requests can no longer bypass replay protection.
- Fixed `SendTransactionAction.configure()` (`action/sendtransactionaction.py`) so the configured `change_address` is written to `self.change_address` instead of overwriting `self.receiving_address`. Previously a supplied change address was silently ignored (change always returned to the sending address) and, when both a receiving address and a change address were configured, the change address would overwrite the intended receiving target, potentially sending the primary payment to the wrong address.
- Base58Check checksum validation for address/private-key decoding is now performed explicitly (raising `TypeError` for non-`str` input and `ValueError` for too-short or invalid-checksum data) instead of using a bare `assert`, so the validation is no longer stripped away under Python's optimized mode (`-O` / `PYTHONOPTIMIZE=1`). The duplicated `b58check_to_bin` implementations in `helpers/privatekeyhelpers.py` and `transactionfactory.py` were consolidated into `helpers/py3specials.py`; invalid Base58Check input now raises `ValueError`/`TypeError` rather than `AssertionError` in callers such as `PrivateKey` and `get_privkey_format`.
- `WebhookAction.run()` (`action/webhookaction.py`) now passes an explicit 10-second `timeout` to `requests.get`/`requests.post` and handles `requests.RequestException` (network errors) by logging the error and returning a failure result instead of raising.
- `WebhookAction.configure()` now rejects non-public webhook URLs via the SSRF-safe `valid_webhook_url` validator, so SSRF-unsafe URLs are rejected at configuration time.
- `CommandAction.run()` (`action/commandaction.py`) and `WebhookAction.run()` (`action/webhookaction.py`) now return a single `bool` (success/failure) as required by the `Action` base-class contract, instead of a tuple. Previously `CommandAction.run()` returned a `(bool, stdout, stderr)` 3-tuple and `WebhookAction.run()` returned a `(bool, text)` 2-tuple, so failed command/webhook actions could be misinterpreted as successful by callers expecting a boolean.

### Security

- Fixed an authentication bypass on the REST API `get_reveal` endpoint (`spellbookserver.py`). The endpoint that returns the reveal-secret value for a `RevealSecretAction` is now protected by `@authentication_required`, so it can no longer be called without a valid API key/signature.
- Fixed a command-injection vulnerability in `spellbookserver.py` (`convert_aac_to_opus`) by removing `shell=True` and passing an argv list to `subprocess.run` (`shell=False`). ffmpeg failures are now surfaced as a `ValueError` (with the decoded stderr) instead of being silently swallowed.
- Fixed a command-injection vulnerability in `action/commandaction.py` (`CommandAction.run`) and `helpers/runcommandprocess.py` (`RunCommandProcess.run`) by removing `shell=True` from command execution.
- Commands are now executed via `shlex.split` + `subprocess.run(..., shell=False)` / `Popen(argv, ...)`, so shell metacharacters in commands and substituted placeholders are no longer interpreted by a shell.
- `CommandAction` now `shlex.quote`s placeholder values before substitution, so untrusted placeholder values cannot inject shell syntax.
- Fixed a command-injection vulnerability in `helpers/setupscripthelpers.py` (`spellbook_call`, `bitcoinwand_call`) by removing `shell=True` from command execution; commands are now passed as an argument list and run with `Popen(args, ..., shell=False)` (the now-unused `format_args` helper was removed from `helpers/platformhelpers.py`).
- Fixed a command-injection vulnerability in `helpers/notify_transaction.py`, which previously built a `curl` shell command from unsanitized CLI arguments (`url`, `pr`, `txid`) and ran it via `Popen(..., shell=True)`. The script now sends the notification with a direct `requests.post(..., json=..., timeout=10)` call (`raise_for_status()` on the response), so no shell is involved and untrusted arguments can no longer inject commands. The file is no longer omitted from coverage in `.coveragerc`.
- `AESCipher` (`AESCipher.py`) now uses authenticated AES-GCM encryption with a salted, slow `scrypt` key-derivation function instead of the previous unauthenticated AES-CBC with PKCS7 padding and a single-round SHA-256 key derivation.
  - Fixes the lack of integrity/authentication: the version byte and salt are authenticated via the GCM tag, so tampering with the ciphertext, tag, salt or version byte is now detected and decryption fails with a `ValueError`.
  - Removes the padding-oracle exposure of the old PKCS7 padding, and the slow `scrypt` KDF makes brute-forcing the wallet password expensive.
  - New ciphertexts use a versioned v2 format (version byte, salt, nonce, tag, ciphertext), and legacy encryption is no longer produced. For backward compatibility, `decrypt()` still reads legacy v1 (AES-CBC) ciphertexts: a payload is tried as v2 first, and one that is not authenticated as v2 is retried as legacy v1 when it is structurally a legacy payload (16-byte IV plus a positive multiple of the 16-byte AES block).
    - The legacy read path returns a decoded UTF-8 string, so a legacy payload whose plaintext is not valid UTF-8 cannot be returned by `decrypt()`.
- Fixed the API nonce replay protection in `authentication.py` to be concurrency-safe and persistent:
  - A module-level `threading.Lock` (`_NONCE_LOCK`) guards the nonce read-modify-write, so the check-and-update of `LAST_NONCES` is atomic and safe under the threaded Bottle server (previously the in-memory nonce map was not protected against concurrent requests).
  - Nonces are now persisted to `json/private/last_nonces.json` via `load_last_nonces()` and `save_last_nonces()`; the file is loaded at import time, so replay protection survives server restarts.
  - The signature is verified before the nonce is recorded (using `hmac.compare_digest`), so an invalid signature can no longer poison the nonce store.
- Webhook URLs configured on `WebhookAction` are now validated with an SSRF-safe `valid_webhook_url` validator (`validators/validators.py`) that rejects URLs resolving to private, loopback, link-local, reserved, multicast, or unspecified addresses (e.g. `10.0.0.0/8`, `127.0.0.0/8`, `169.254.0.0/16`, `0.0.0.0`, `::1`), preventing server-side request forgery against internal services.

### Internal

- Applied 1,575 ruff safe auto-fixes across the codebase.
- Added type annotations and fixed mypy errors across the codebase.
- Removed dead code with vulture and added a `vulture_whitelist.py` file to whitelist framework hooks, dynamic-plugin APIs, and injected pytest fixtures. Deleted the top-level `__init__.py`.
- Made unit tests self-contained and runnable in a fresh clone, and expanded test coverage.
- Added `.SWE/` to `.gitignore` for SWE pipeline artifacts.
