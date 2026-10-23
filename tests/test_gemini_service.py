import logging
from types import SimpleNamespace

import pytest

from app.config.settings import Settings
from app.services import gemini_service as gemini_service_module
from app.services.gemini_service import GeminiService, GeminiServiceError


class FakeModels:
    def __init__(self, response):
        self.response = response
        self.request = None

    def generate_content(self, **request):
        self.request = request
        return self.response


def test_generate_answer_sends_prompt_history_and_settings():
    models = FakeModels(SimpleNamespace(text="A helpful answer."))
    client = SimpleNamespace(models=models)
    settings = Settings(api_key="test-key", model="test-model", temperature=0.4)
    history = [
        {"role": "user", "content": "Question?"},
        {"role": "assistant", "content": "Earlier answer."},
    ]

    answer = GeminiService(settings, client=client).generate_answer(history)

    assert answer == "A helpful answer."
    assert models.request["model"] == "test-model"
    assert models.request["config"].temperature == 0.4
    system_instruction = models.request["config"].system_instruction
    assert "Answer the user's question clearly." in system_instruction
    assert "do not fabricate facts" in system_instruction
    assert "conversation history" in system_instruction
    assert [
        (content.role, content.parts[0].text)
        for content in models.request["contents"]
    ] == [
        ("user", "Question?"),
        ("model", "Earlier answer."),
    ]


def test_service_initializes_gemini_client_with_configured_key(monkeypatch):
    created_clients = []

    class FakeClient:
        def __init__(self, *, api_key):
            created_clients.append(api_key)

    monkeypatch.setattr(gemini_service_module.genai, "Client", FakeClient)
    settings = Settings(
        api_key="configured-test-key",
        model="test-model",
        temperature=0.4,
    )

    GeminiService(settings)

    assert created_clients == ["configured-test-key"]


def test_generate_answer_rejects_empty_response():
    client = SimpleNamespace(models=FakeModels(SimpleNamespace(text=None)))
    settings = Settings(api_key="test-key", model="test-model", temperature=0.4)

    with pytest.raises(GeminiServiceError, match="empty response"):
        GeminiService(settings, client=client).generate_answer([])


def test_generate_answer_sanitizes_api_error(monkeypatch, caplog):
    class FakeAPIError(Exception):
        pass

    models = FakeModels(None)

    def raise_api_error(**request):
        del request
        raise FakeAPIError("sensitive SDK details")

    models.generate_content = raise_api_error
    monkeypatch.setattr(gemini_service_module, "APIError", FakeAPIError)
    client = SimpleNamespace(models=models)
    settings = Settings(api_key="secret-test-key", model="test-model", temperature=0.4)

    caplog.set_level(logging.ERROR)
    with pytest.raises(GeminiServiceError) as error:
        GeminiService(settings, client=client).generate_answer(
            [{"role": "user", "content": "private conversation text"}]
        )

    assert "sensitive SDK details" not in str(error.value)
    assert "secret-test-key" not in str(error.value)
    assert error.value.__suppress_context__
    assert "sensitive SDK details" not in caplog.text
    assert "secret-test-key" not in caplog.text
    assert "private conversation text" not in caplog.text
    assert "FakeAPIError" in caplog.text
