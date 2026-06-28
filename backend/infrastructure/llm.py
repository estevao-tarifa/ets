import logging

import litellm

logger = logging.getLogger(__name__)


async def call_llm(
    prompt: str,
    provider: str,
    api_key: str,
    model: str,
    max_tokens: int = 2048,
    json_mode: bool = False,
) -> str:
    logger.info(f"LLM call: provider={provider} model={model}")
    full_model = model if "/" in model else f"{provider}/{model}"
    kwargs: dict = {
        "model": full_model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "api_key": api_key,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    response = await litellm.acompletion(**kwargs)
    return response.choices[0].message.content


async def test_connection(
    provider: str, api_key: str, model: str
) -> dict[str, bool | str]:
    try:
        await call_llm(prompt="ping", provider=provider, api_key=api_key, model=model, max_tokens=5)
        return {"ok": True}
    except Exception as e:
        logger.warning(f"LLM connection test failed: provider={provider} model={model} error={e}")
        return {"ok": False, "error": str(e)}
