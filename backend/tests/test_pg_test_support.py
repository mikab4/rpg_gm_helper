from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from tests import pg_test_support


def test_load_test_settings_uses_runtime_database_url_without_env_files(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    # Arrange
    missing_env_file = tmp_path / ".env.test"
    missing_example_file = tmp_path / ".env.test.example"
    runtime_database_url = "postgresql+psycopg://postgres:postgres@127.0.0.1:55432/rpg_gm_helper"
    monkeypatch.setattr(pg_test_support, "TEST_ENV_FILE", missing_env_file)
    monkeypatch.setattr(pg_test_support, "TEST_ENV_EXAMPLE_FILE", missing_example_file)

    # Act
    settings = pg_test_support.load_test_settings(runtime_database_url=runtime_database_url)

    # Assert
    assert settings.database_url == runtime_database_url


def test_ensure_postgres_test_container_returns_runtime_database_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Arrange
    recorded_commands: list[list[str]] = []

    def fake_run(
        command: list[str],
        *,
        check: bool,
        capture_output: bool,
        text: bool,
    ) -> subprocess.CompletedProcess[str]:
        del check, capture_output, text
        recorded_commands.append(command)
        if command[:2] == ["docker", "version"]:
            return subprocess.CompletedProcess(command, 0, stdout="26.1.0\n", stderr="")
        if command[:2] == ["docker", "run"]:
            return subprocess.CompletedProcess(command, 0, stdout="container-id\n", stderr="")
        if command[:2] == ["docker", "port"]:
            return subprocess.CompletedProcess(
                command,
                0,
                stdout="127.0.0.1:55432\n",
                stderr="",
            )
        raise AssertionError(f"Unexpected command: {command}")

    monkeypatch.setattr(pg_test_support.subprocess, "run", fake_run)
    monkeypatch.setattr(pg_test_support, "wait_for_postgres_ready", lambda database_url: None)

    # Act
    runtime_container = pg_test_support.ensure_postgres_test_container()

    # Assert
    assert runtime_container.database_url == (
        "postgresql+psycopg://postgres:postgres@127.0.0.1:55432/rpg_gm_helper"
    )
    assert runtime_container.container_name.startswith(pg_test_support.POSTGRES_TEST_CONTAINER_PREFIX)
    assert recorded_commands[1][-1] == pg_test_support.POSTGRES_TEST_IMAGE


def test_ensure_postgres_test_container_fails_when_docker_cli_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Arrange
    def missing_docker(
        command: list[str],
        *,
        check: bool,
        capture_output: bool,
        text: bool,
    ) -> subprocess.CompletedProcess[str]:
        del command, check, capture_output, text
        raise FileNotFoundError

    monkeypatch.setattr(pg_test_support.subprocess, "run", missing_docker)

    # Act / Assert
    with pytest.raises(pg_test_support.PostgresTestHarnessError, match="Docker CLI is not installed"):
        pg_test_support.ensure_postgres_test_container()


def test_ensure_postgres_test_container_fails_when_docker_daemon_is_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Arrange
    def unavailable_docker(
        command: list[str],
        *,
        check: bool,
        capture_output: bool,
        text: bool,
    ) -> subprocess.CompletedProcess[str]:
        del check, capture_output, text
        if command[:2] == ["docker", "version"]:
            raise subprocess.CalledProcessError(
                1,
                command,
                output="",
                stderr="Cannot connect to the Docker daemon at unix:///var/run/docker.sock",
            )
        raise AssertionError(f"Unexpected command: {command}")

    monkeypatch.setattr(pg_test_support.subprocess, "run", unavailable_docker)

    # Act / Assert
    with pytest.raises(
        pg_test_support.PostgresTestHarnessError,
        match="Docker is installed but the daemon is unavailable",
    ):
        pg_test_support.ensure_postgres_test_container()


def test_ensure_postgres_test_container_reports_missing_wsl_integration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Arrange
    def unavailable_docker_in_wsl(
        command: list[str],
        *,
        check: bool,
        capture_output: bool,
        text: bool,
    ) -> subprocess.CompletedProcess[str]:
        del check, capture_output, text
        if command[:2] == ["docker", "version"]:
            raise subprocess.CalledProcessError(
                1,
                command,
                output=(
                    "The command 'docker' could not be found in this WSL 2 distro.\n"
                    "We recommend to activate the WSL integration in Docker Desktop settings.\n"
                ),
                stderr="",
            )
        raise AssertionError(f"Unexpected command: {command}")

    monkeypatch.setattr(pg_test_support.subprocess, "run", unavailable_docker_in_wsl)

    # Act / Assert
    with pytest.raises(
        pg_test_support.PostgresTestHarnessError,
        match="Enable Docker Desktop WSL integration",
    ):
        pg_test_support.ensure_postgres_test_container()
