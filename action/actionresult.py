#!/usr/bin/env python

"""Unified return type for all Spellbook actions."""

from collections.abc import Iterator
from dataclasses import dataclass


@dataclass(eq=False)
class ActionResult:
    """
    Unified result object returned by every Spellbook action's ``run()`` method.

    The object is designed to behave like the tuple/bool values that actions
    previously returned, so existing call sites keep working unchanged:

    - Truthiness (``if result:``) reflects ``success`` via ``__bool__``.
    - Tuple unpacking (``ok, out, err = result``) works via ``__iter__``.
    - Indexing (``result[0]``) and ``len(result) == 3`` work via ``__getitem__``
      and ``__len__``.
    - Explicit attributes (``result.success``, ``result.stdout``, ``result.stderr``)
      are discoverable.

    :param success: Whether the action completed successfully
    :param stdout: Standard output produced by the action (either ``str`` or ``bytes``)
    :param stderr: Standard error produced by the action (either ``str`` or ``bytes``)
    """

    success: bool
    stdout: str | bytes = ""
    stderr: str | bytes = ""

    def __bool__(self) -> bool:
        """
        Return the success flag so the result can be used in truthiness checks.

        :return: True if the action succeeded, False otherwise
        """
        return self.success

    def __iter__(self) -> Iterator[bool | str | bytes]:
        """
        Iterate over the result so it can be unpacked like a 3-tuple.

        :return: An iterator yielding success, stdout and stderr in that order
        """
        yield self.success
        yield self.stdout
        yield self.stderr

    def __getitem__(self, index: int) -> bool | str | bytes:
        """
        Support indexing into the result as if it were a 3-tuple.

        :param index: The position to retrieve (0 for success, 1 for stdout, 2 for stderr)
        :return: The value at the given position
        """
        return (self.success, self.stdout, self.stderr)[index]

    def __eq__(self, other: object) -> bool:
        """
        Compare this result to another ActionResult or to a tuple.

        A shorter tuple is compared against the leading elements of this result,
        so a 2-tuple like ``(success, stdout)`` matches regardless of ``stderr``.

        :param other: An ActionResult, a tuple, or any other value
        :return: True if the values are equal, False if they are not, and
                 NotImplemented for incomparable types
        """
        if isinstance(other, ActionResult):
            return (self.success, self.stdout, self.stderr) == (other.success, other.stdout, other.stderr)
        if isinstance(other, tuple):
            return (self.success, self.stdout, self.stderr)[:len(other)] == other
        return NotImplemented

    # Instances are intentionally unhashable. A custom ``__eq__`` normally
    # sets ``__hash__`` to None implicitly; we declare it explicitly because the
    # tuple-prefix comparison semantics cannot be reconciled with a consistent
    # hash (equal objects must have equal hashes, but an ActionResult can equal
    # many different tuples of varying lengths).
    __hash__ = None  # type: ignore[assignment]

    def __len__(self) -> int:
        """
        Return the number of fields in the result.

        :return: 3 (success, stdout and stderr)
        """
        return 3

    def json_encodable(self) -> list:
        """
        Return a plain JSON-serializable representation of the result.

        :return: A list containing ``[success, stdout, stderr]``
        """
        return [self.success, self.stdout, self.stderr]
