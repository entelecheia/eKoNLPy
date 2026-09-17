from click.testing import CliRunner

from ekonlpy.__cli__ import main


def test_cli_without_input_prints_help():
    result = CliRunner().invoke(main, [])

    assert result.exit_code == 0
    assert "Usage" in result.output


def test_cli_with_input_tags_korean_text():
    result = CliRunner().invoke(main, ["--input", "한국은행이 금리를 인상했다"])

    assert result.exit_code == 0
    assert "한국은행" in result.output
    assert "NNG" in result.output or "NNP" in result.output


def test_cli_with_mecab_tagger_uses_original_tagger():
    result = CliRunner().invoke(main, ["-t", "mecab", "-i", "금리 인상"])

    assert result.exit_code == 0
    assert "금리" in result.output


def test_cli_version_option():
    result = CliRunner().invoke(main, ["--version"])

    assert result.exit_code == 0
