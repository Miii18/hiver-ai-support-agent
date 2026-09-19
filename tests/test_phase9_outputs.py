"""Phase 9: Production Frontend + Deployment tests."""
from __future__ import annotations

import json
from pathlib import Path

import pytest


class TestPhase9Files:
    """Verify all Phase 9 files exist."""

    def test_ui_files_exist(self) -> None:
        """UI module files should exist."""
        required = [
            "src/ui/__init__.py",
            "src/ui/streamlit_app.py",
            "src/ui/api_client.py",
            "src/ui/components.py",
            "src/ui/theme.py",
        ]
        for path in required:
            assert Path(path).exists(), f"Missing: {path}"

    def test_docker_files_exist(self) -> None:
        """Docker configuration files should exist."""
        required = [
            "docker/Dockerfile.backend",
            "docker/Dockerfile.frontend",
            "docker/docker-compose.yml",
            "docker/.dockerignore",
        ]
        for path in required:
            assert Path(path).exists(), f"Missing: {path}"

    def test_deployment_files_exist(self) -> None:
        """Deployment configuration files should exist."""
        required = [
            "deployment/render.yaml",
            "deployment/railway.toml",
        ]
        for path in required:
            assert Path(path).exists(), f"Missing: {path}"

    def test_scripts_exist(self) -> None:
        """Run scripts should exist."""
        required = [
            "scripts/run_streamlit.py",
            "scripts/run_phase9.py",
        ]
        for path in required:
            assert Path(path).exists(), f"Missing: {path}"

    def test_test_files_exist(self) -> None:
        """Test files should exist."""
        assert Path("tests/test_phase9_outputs.py").exists()


class TestPhase9Imports:
    """Verify Phase 9 modules import correctly."""

    def test_api_client_imports(self) -> None:
        """API client module should import."""
        from src.ui import api_client

        assert hasattr(api_client, "health_check")
        assert hasattr(api_client, "fetch_intents")
        assert hasattr(api_client, "chat")
        assert hasattr(api_client, "reset_memory")

    def test_components_imports(self) -> None:
        """Components module should import."""
        from src.ui import components

        assert hasattr(components, "status_pill")
        assert hasattr(components, "intent_badge")
        assert hasattr(components, "confidence_meter")
        assert hasattr(components, "render_chat_bubble")
        assert hasattr(components, "render_source_card")
        assert hasattr(components, "render_sources")

    def test_theme_imports(self) -> None:
        """Theme module should import."""
        from src.ui import theme

        assert hasattr(theme, "apply_theme")

    def test_streamlit_imports(self) -> None:
        """Streamlit app should import."""
        # Note: full import may require streamlit context, so we just check the file exists
        app_path = Path("src/ui/streamlit_app.py")
        assert app_path.exists()
        content = app_path.read_text()
        assert "initialize_state" in content
        assert "app_header" in content
        assert "render_main" in content


class TestDockerConfiguration:
    """Verify Docker configuration is valid."""

    def test_dockerfile_backend_valid(self) -> None:
        """Backend Dockerfile should have required directives."""
        content = Path("docker/Dockerfile.backend").read_text()
        assert "FROM python:3.11" in content
        assert "WORKDIR /app" in content
        assert "EXPOSE 8000" in content
        assert "CMD" in content
        assert "scripts/run_api.py" in content

    def test_dockerfile_frontend_valid(self) -> None:
        """Frontend Dockerfile should have required directives."""
        content = Path("docker/Dockerfile.frontend").read_text()
        assert "FROM python:3.11" in content
        assert "WORKDIR /app" in content
        assert "EXPOSE 8501" in content
        assert "CMD" in content
        assert "scripts/run_streamlit.py" in content

    def test_docker_compose_valid(self) -> None:
        """docker-compose.yml should have required services."""
        import yaml

        content = Path("docker/docker-compose.yml").read_text()
        config = yaml.safe_load(content)
        assert "services" in config
        assert "backend" in config["services"]
        assert "frontend" in config["services"]

    def test_dockerignore_exists(self) -> None:
        """.dockerignore should have standard exclusions."""
        content = Path("docker/.dockerignore").read_text()
        assert "__pycache__" in content
        assert ".git" in content


class TestDeploymentConfiguration:
    """Verify deployment configuration files."""

    def test_render_yaml_valid(self) -> None:
        """render.yaml should be valid YAML."""
        import yaml

        content = Path("deployment/render.yaml").read_text()
        config = yaml.safe_load(content)
        assert "services" in config
        assert len(config["services"]) >= 1

    def test_railway_toml_valid(self) -> None:
        """railway.toml should be valid TOML."""
        import tomli as toml

        content = Path("deployment/railway.toml").read_text()
        config = toml.loads(content)
        assert "build" in config or "services" in config


class TestReadme:
    """Verify README has Phase 9 documentation."""

    def test_readme_has_phase9_section(self) -> None:
        """README should have Phase 9 section."""
        content = Path("README.md").read_text()
        assert "Phase 9" in content or "phase 9" in content.lower()
