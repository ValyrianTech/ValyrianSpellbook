#!/usr/bin/env python
import os

import pytest

from helpers.pathhelpers import safe_path


class TestSafePath:
    """Tests for the fail-closed safe_path helper."""

    @pytest.mark.parametrize('candidate', ['../x', 'a/../../b', '..'])
    def test_rejects_parent_directory_traversal(self, candidate):
        with pytest.raises(ValueError):
            safe_path('/tmp', candidate)

    @pytest.mark.parametrize('candidate', ['/etc/passwd', '/tmp/foo'])
    def test_rejects_absolute_path(self, candidate):
        with pytest.raises(ValueError):
            safe_path('/tmp', candidate)

    @pytest.mark.parametrize('candidate', [None, 123, b'x', ''])
    def test_rejects_none_non_string_and_empty(self, candidate):
        with pytest.raises(ValueError):
            safe_path('/tmp', candidate)

    def test_rejects_symlink_escape(self, tmp_path):
        base = tmp_path / 'base'
        base.mkdir()
        outside = tmp_path / 'outside'
        outside.mkdir()
        (outside / 'file.txt').write_text('secret')
        link = base / 'link'
        link.symlink_to(outside)

        with pytest.raises(ValueError):
            safe_path(str(base), 'link/file.txt')

    def test_accepts_nested_name(self, tmp_path):
        base = tmp_path / 'base'
        sub = base / 'sub'
        sub.mkdir(parents=True)
        (sub / 'file.txt').write_text('content')

        result = safe_path(str(base), 'sub/file.txt')
        assert result == os.path.realpath(str(sub / 'file.txt'))

    @pytest.mark.parametrize('candidate', ['foo.bar', 'a.b.c'])
    def test_accepts_dotted_non_traversal_names(self, tmp_path, candidate):
        base = tmp_path / 'base'
        base.mkdir()

        result = safe_path(str(base), candidate)
        assert result == os.path.realpath(str(base / candidate))

    def test_accepts_plain_name(self, tmp_path):
        base = tmp_path / 'base'
        base.mkdir()

        result = safe_path(str(base), 'file.txt')
        assert result == os.path.realpath(str(base / 'file.txt'))

    def test_returns_absolute_real_resolved_path(self, tmp_path):
        base = tmp_path / 'base'
        base.mkdir()

        result = safe_path(str(base), 'file.txt')
        assert os.path.isabs(result)
        assert result == os.path.realpath(str(base / 'file.txt'))

    def test_tolerates_symlinked_base(self, tmp_path):
        base = tmp_path / 'base'
        base.mkdir()
        (base / 'file.txt').write_text('content')
        link = tmp_path / 'link'
        link.symlink_to(base)

        result = safe_path(str(link), 'file.txt')
        assert result == os.path.realpath(str(base / 'file.txt'))

    def test_accepts_pathlike_base_dir(self, tmp_path):
        base = tmp_path / 'base'
        base.mkdir()

        result = safe_path(base, 'file.txt')
        assert result == os.path.realpath(str(base / 'file.txt'))
