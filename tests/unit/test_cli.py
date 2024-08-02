import pytest
from typer.testing import CliRunner

import cli
from cli import app


runner = CliRunner()


def test_help():
    result = runner.invoke(app, ['--help'])
    assert result.exit_code == 0


@pytest.mark.skip(reason="old data in db")
def test_stats():
    result = runner.invoke(app, ['stats'])
    assert result.exit_code == 0
    assert len(result.stdout) > 100
