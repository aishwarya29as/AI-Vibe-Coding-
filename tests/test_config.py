import pytest

import app.config.settings as settings_module
from app.config.settings import SettingsError, load_settings


def ignore_dotenv(*, dotenv_path):
    return dotenv_path.exists()


def test_load_settings_defaults_and_api_key(monkeypatch, tmp_path):
    monkeypatch.setattr(settings_module, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(settings_module, "load_dotenv", ignore_dotenv)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    monkeypatch.delenv("TEMPERATURE", raising=False)

    settings = load_settings()

    assert settings.api_key == "test-key"
    assert settings.model == "gemini-3.8-flash"
    assert settings.temperature == 0.2


def test_load_settings_reads_isolated_dotenv_file(monkeypatch, tmp_path):
    monkeypatch.setattr(settings_module, "PROJECT_ROOT", tmp_path)
    (tmp_path / ".env").write_text(
        "GEMINI_API_KEY=isolated-test-key\n"
        "GEMINI_MODEL=gemini-test-model\n"
        "TEMPERATURE=0.2\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    monkeypatch.delenv("TEMPERATURE", raising=False)

    settings = load_settings()

    assert settings.api_key == "isolated-test-key"
    assert settings.model == "gemini-test-model"
    assert settings.temperature == 0.2


def test_load_settings_requires_api_key(monkeypatch, tmp_path):
    monkeypatch.setattr(settings_module, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(settings_module, "load_dotenv", ignore_dotenv)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with pytest.raises(SettingsError, match="Create a .env file"):
        load_settings()


@pytest.mark.parametrize("raw_temperature", ["2.1", "nan", "inf", "not-a-number"])
def test_load_settings_rejects_invalid_temperature(monkeypatch, tmp_path, raw_temperature):
    monkeypatch.setattr(settings_module, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(settings_module, "load_dotenv", ignore_dotenv)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("TEMPERATURE", raw_temperature)

    with pytest.raises(SettingsError, match="TEMPERATURE must be a number"):
        load_settings()


def test_settings_repr_does_not_contain_api_key(monkeypatch, tmp_path):
    monkeypatch.setattr(settings_module, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(settings_module, "load_dotenv", ignore_dotenv)
    monkeypatch.setenv("GEMINI_API_KEY", "secret-test-key")

    assert "secret-test-key" not in repr(load_settings())
