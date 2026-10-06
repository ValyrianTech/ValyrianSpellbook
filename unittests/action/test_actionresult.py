#!/usr/bin/env python
from action.actionresult import ActionResult


class TestActionResult:
    """Tests for the ActionResult dataclass."""

    def test_default_stdout_and_stderr_are_empty(self):
        result = ActionResult(success=True)
        assert result.stdout == ''
        assert result.stderr == ''

    def test_bool_true(self):
        assert ActionResult(success=True)

    def test_bool_false(self):
        assert not ActionResult(success=False)

    def test_iter_unpacks_into_three_values(self):
        ok, out, err = ActionResult(success=True, stdout='out', stderr='err')
        assert ok is True
        assert out == 'out'
        assert err == 'err'

    def test_len_is_three(self):
        assert len(ActionResult(success=False)) == 3

    def test_getitem_indexing(self):
        result = ActionResult(success=True, stdout='out', stderr='err')
        assert result[0] is True
        assert result[1] == 'out'
        assert result[2] == 'err'

    def test_eq_equal_action_result(self):
        assert ActionResult(True, 'out', 'err') == ActionResult(True, 'out', 'err')

    def test_eq_unequal_action_result(self):
        assert ActionResult(True, 'out', 'err') != ActionResult(False, 'out', 'err')

    def test_eq_equal_tuple(self):
        assert ActionResult(True, 'out', 'err') == (True, 'out', 'err')

    def test_eq_unequal_tuple(self):
        assert ActionResult(True, 'out', 'err') != (False, 'out', 'err')

    def test_eq_shorter_tuple_prefix_matches(self):
        assert ActionResult(True, 'out', '') == (True, 'out')
        assert ActionResult(True, 'out', 'err') == (True, 'out')

    def test_eq_shorter_tuple_unequal(self):
        assert (ActionResult(True, 'out', '') == (False, 'out')) is False

    def test_eq_non_tuple_returns_notimplemented(self):
        assert ActionResult(success=True).__eq__(5) is NotImplemented

    def test_json_encodable(self):
        result = ActionResult(success=True, stdout='out', stderr='err')
        assert result.json_encodable() == [True, 'out', 'err']
