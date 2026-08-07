#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for webui.main FastAPI app."""
from unittest.mock import patch, MagicMock


class TestAppConfiguration:
    def test_app_title(self, app):
        assert app.title == "Valyrian Spellbook Admin"

    def test_app_version(self, app):
        assert app.version == "1.0.0"

    def test_app_description(self, app):
        assert "Web UI" in app.description

    def test_routers_included(self, app):
        routes = [r.path for r in app.routes]
        assert "/" in routes
        assert "/login" in routes
        assert "/logout" in routes
        # Router-prefixed routes
        assert any(r.startswith("/triggers") for r in routes)
        assert any(r.startswith("/actions") for r in routes)
        assert any(r.startswith("/llms") for r in routes)
        assert any(r.startswith("/explorers") for r in routes)
        assert any(r.startswith("/blockchain") for r in routes)


class TestExceptionHandlers:
    def test_404_handler(self, client):
        response = client.get("/nonexistent-page", follow_redirects=False)
        assert response.status_code == 404

    def test_500_handler(self, app):
        # Trigger a 500 by mocking a route to raise
        with patch("routers.dashboard.is_authenticated", return_value=True):
            with patch("routers.dashboard.get_api_client") as mock_get_client:
                mock_client = MagicMock()
                mock_client.get_triggers.side_effect = Exception("test error")
                mock_client.get_actions.return_value = []
                mock_client.get_llms.return_value = []
                mock_client.get_explorers.return_value = []
                mock_client.ping.return_value = {"success": True}
                mock_client.get_latest_block.return_value = {}
                mock_get_client.return_value = mock_client
                from starlette.testclient import TestClient
                with TestClient(app, raise_server_exceptions=False) as c:
                    response = c.get("/", follow_redirects=False)
                    assert response.status_code == 500


class TestMainModule:
    def test_main_importable(self):
        import main as main_module
        assert hasattr(main_module, "app")

    def test_templates_dir(self):
        import main as main_module
        assert hasattr(main_module, "templates")

    def test_static_mount(self, app):
        routes = [r.path for r in app.routes]
        assert "/static" in routes

    def test_main_block_runs_uvicorn(self, mock_settings):
        """Cover the if __name__ == '__main__' block."""
        with patch("uvicorn.run") as mock_run:
            import main as main_module
            with open(main_module.__file__) as f:
                code = f.read()
            exec(compile(code, main_module.__file__, "exec"), {"__name__": "__main__", "__file__": main_module.__file__})
            mock_run.assert_called_once()
            call_kwargs = mock_run.call_args[1]
            assert call_kwargs["host"] == "127.0.0.1"
            assert call_kwargs["port"] == 5001
