# Vulture whitelist. Every identifier referenced below is treated as "used"
# by vulture. Module-level PEP 562 __getattr__ hooks are framework magic and
# provide a public API (data.EXPLORER) that static analysis cannot see.

data.__getattr__  # noqa  # pragma: no cover - vulture whitelist entry; never executed (static-analysis only)
