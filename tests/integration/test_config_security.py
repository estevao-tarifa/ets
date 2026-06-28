from unittest.mock import AsyncMock, patch

import pytest

from backend.api.routes.config import ConfigOut, get_config
from backend.infrastructure.config import Settings
from backend.infrastructure.llm import test_connection as llm_test_connection


@pytest.mark.asyncio
async def test_config_out_hint_only_last_4():
    full_key = "sk-prod-supersecret1234"
    hint = ("..." + full_key[-4:]) if len(full_key) >= 4 else "****"
    out = ConfigOut(provider="groq", model="llama3", api_key_hint=hint)

    assert full_key not in out.api_key_hint
    assert out.api_key_hint.endswith("1234")
    assert len(out.api_key_hint) == 7  # "..." + 4 chars


@pytest.mark.asyncio
async def test_test_connection_success_never_returns_key():
    api_key = "sk-secret-key-xyz9876"
    with patch("backend.infrastructure.llm.litellm.acompletion", new_callable=AsyncMock) as m:
        m.return_value.choices[0].message.content = "pong"
        result = await llm_test_connection("groq", api_key, "llama3")

    assert api_key not in str(result)
    assert result.get("ok") is True


@pytest.mark.asyncio
async def test_test_connection_error_never_leaks_key():
    api_key = "sk-secret-key-xyz9876"
    with patch("backend.infrastructure.llm.litellm.acompletion", new_callable=AsyncMock) as m:
        m.side_effect = Exception("Connection refused")
        result = await llm_test_connection("groq", api_key, "llama3")

    assert api_key not in str(result)
    assert result.get("ok") is False


@pytest.mark.asyncio
async def test_get_config_hint_hides_full_key():
    fake_key = "sk-verysecretkeyabcd"
    fake_settings = Settings(LLM_PROVIDER="groq", LLM_API_KEY=fake_key, LLM_MODEL="llama3")
    with patch("backend.api.routes.config.get_settings", return_value=fake_settings):
        result = await get_config()

    assert fake_key not in result.api_key_hint
    assert result.api_key_hint.endswith("abcd")
    assert result.provider == "groq"
    assert result.model == "llama3"
