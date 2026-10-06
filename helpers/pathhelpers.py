#!/usr/bin/env python
"""Shared fail-closed path validation helpers."""

import os
from pathlib import Path


def safe_path(base_dir, candidate):
    """Resolve a candidate path against a trusted base directory, failing closed.

    This is a security helper for constraining untrusted (user/agent-supplied)
    file names to a trusted directory. On success it returns the canonical,
    absolute, resolved path string. On any violation it raises ``ValueError``
    with a clear message instead of returning a path.

    The candidate is rejected (``ValueError``) when:

    - it is ``None``, not a ``str``, or an empty string;
    - it contains a ``..`` path segment (so ``../x``, ``a/../b`` and ``..`` are
      all rejected);
    - it is an absolute path (``os.path.isabs``);
    - it resolves (after following symlinks) outside the base directory.

    The base directory is resolved first with ``os.path.realpath`` so that
    symlinks in the base are followed and the base is canonical. The candidate
    is then resolved relative to that canonical base and must remain within it
    (checked with ``pathlib.Path.is_relative_to``), which also rejects symlink
    escapes because ``realpath`` is applied to the candidate. The target file is
    not required to exist; callers may check existence themselves.

    :param base_dir: The trusted base directory (str or os.PathLike).
    :param candidate: The untrusted, typically relative, file name (str).
    :return: The verified, resolved absolute path string.
    :raises ValueError: If the candidate is invalid or escapes the base.
    """
    if candidate is None or not isinstance(candidate, str) or candidate == '':
        raise ValueError(f'Invalid path: {candidate!r}')

    if '..' in Path(candidate).parts:
        raise ValueError(f'Invalid path: {candidate!r} contains a parent directory segment')

    if os.path.isabs(candidate):
        raise ValueError(f'Invalid path: {candidate!r} is an absolute path')

    base_resolved = os.path.realpath(base_dir)
    resolved_candidate = os.path.realpath(os.path.join(base_resolved, candidate))

    if not Path(resolved_candidate).is_relative_to(Path(base_resolved)):
        raise ValueError(f'Invalid path: {candidate!r} escapes base directory {base_resolved!r}')

    return resolved_candidate
