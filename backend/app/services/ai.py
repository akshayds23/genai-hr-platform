import logging
import os

logger = logging.getLogger(__name__)


class AIUnavailableError(Exception):
    """Raised when the AI service is not configured or unavailable."""


class AIRateLimitError(Exception):
    """Raised when daily AI limit is exceeded."""


def check_and_increment_ai_usage(user_id: int | None = None) -> None:
    """Check and increment daily AI usage per user and globally."""
    try:
        from datetime import date
        from flask import has_request_context
        from flask_security import current_user
        from app.models.models import AIUsage, db

        if not has_request_context():
            return

        demo_mode = str(_get_config("DEMO_MODE", "false")).lower() in ("1", "true", "yes")
        if not demo_mode:
            return

        if user_id is None:
            if current_user and getattr(current_user, "is_authenticated", False):
                user_id = current_user.id

        today = date.today()

        user_limit = int(_get_config("AI_DAILY_LIMIT", "20") or 20)
        global_limit = int(_get_config("AI_GLOBAL_DAILY_LIMIT", "300") or 300)

        # Global check
        global_count = db.session.query(db.func.sum(AIUsage.count)).filter(AIUsage.day == today).scalar() or 0
        if global_count >= global_limit:
            raise AIRateLimitError("Daily AI limit reached for this demo account. Try again tomorrow.")

        if user_id:
            record = AIUsage.query.filter_by(user_id=user_id, day=today).first()
            if record and record.count >= user_limit:
                raise AIRateLimitError("Daily AI limit reached for this demo account. Try again tomorrow.")
            if record:
                record.count += 1
            else:
                record = AIUsage(user_id=user_id, day=today, count=1)
                db.session.add(record)
            db.session.commit()
    except AIRateLimitError:
        raise
    except Exception as exc:
        logger.warning("Could not record/check AI usage: %s", exc)


_client = None
_cached_api_key: str | None = None
_active_gemini_model: str | None = None


def _get_config(key: str, default: str | None = None) -> str | None:
    val = os.getenv(key)
    if val:
        return val
    try:
        from flask import current_app
        if current_app:
            return current_app.config.get(key, default)
    except Exception:
        pass
    return default


def get_embedding_model_name() -> str:
    return _get_config("GEMINI_EMBED_MODEL", "gemini-embedding-001") or "gemini-embedding-001"


def _get_active_gemini_model() -> str:
    global _active_gemini_model
    if _active_gemini_model:
        return _active_gemini_model
    _active_gemini_model = _get_config("GEMINI_MODEL", "gemini-3.1-flash-lite") or "gemini-3.1-flash-lite"
    return _active_gemini_model


def _set_active_gemini_model(model_name: str) -> None:
    global _active_gemini_model
    _active_gemini_model = model_name


def _get_gemini_client(api_key: str):
    global _client, _cached_api_key
    if _client is not None and _cached_api_key == api_key:
        return _client
    from google import genai
    _client = genai.Client(api_key=api_key)
    _cached_api_key = api_key
    return _client


def _discover_fallback_gemini_model(client) -> str | None:
    try:
        available_models = [m.name for m in client.models.list()]
        candidates = []
        for name in available_models:
            clean_name = name.replace("models/", "")
            # Only flash models, excluding 1.5 and gemini-pro
            if "flash" in clean_name and "1.5" not in clean_name and "pro" not in clean_name:
                candidates.append(clean_name)
        if candidates:
            for preferred in ["gemini-3.1-flash-lite", "gemini-2.5-flash", "gemini-2.0-flash"]:
                if preferred in candidates:
                    return preferred
            return candidates[0]
    except Exception as exc:
        logger.warning("Could not list available Gemini models: %s", exc)
    return None


def _generate_with_groq(
    prompt: str,
    system: str | None = None,
    json_output: bool = False,
    max_tokens: int = 1024,
) -> str:
    groq_key = _get_config("GROQ_API_KEY")
    if not groq_key:
        return ""
    groq_model = _get_config("GROQ_MODEL", "openai/gpt-oss-20b") or "openai/gpt-oss-20b"
    try:
        from openai import OpenAI
        client = OpenAI(api_key=groq_key, base_url="https://api.groq.com/openai/v1")
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response_format = {"type": "json_object"} if json_output else None
        kwargs = {
            "model": groq_model,
            "messages": messages,
            "max_tokens": max_tokens,
        }
        if response_format:
            kwargs["response_format"] = response_format

        resp = client.chat.completions.create(**kwargs)
        if resp.choices and resp.choices[0].message and resp.choices[0].message.content:
            return resp.choices[0].message.content.strip()
    except Exception as exc:
        logger.warning("Groq chat completion failed: %s; trying responses API", exc)
        try:
            from openai import OpenAI
            client = OpenAI(api_key=groq_key, base_url="https://api.groq.com/openai/v1")
            resp = client.responses.create(
                input=prompt,
                model=groq_model,
                max_output_tokens=max_tokens,
            )
            text = getattr(resp, "output_text", "") or ""
            return text.strip()
        except Exception as exc2:
            logger.warning("Groq fallback also failed: %s", exc2)
            raise exc

    return ""


def _real_generate_text(
    prompt: str,
    *,
    system: str | None = None,
    json_output: bool = False,
    max_tokens: int = 1024,
) -> str:
    check_and_increment_ai_usage()
    import sys
    ai_mod = sys.modules.get("app.services.ai")
    if ai_mod and getattr(ai_mod, "generate_text", None) is not _real_generate_text:
        return ai_mod.generate_text(
            prompt, system=system, json_output=json_output, max_tokens=max_tokens
        )

    gemini_key = _get_config("GEMINI_API_KEY")
    groq_key = _get_config("GROQ_API_KEY")

    if not gemini_key and not groq_key:
        raise AIUnavailableError("No AI API key is configured (neither GEMINI_API_KEY nor GROQ_API_KEY).")

    gemini_error = None
    if gemini_key:
        try:
            client = _get_gemini_client(gemini_key)
            model_name = _get_active_gemini_model()

            from google.genai import types
            config_kwargs = {
                "max_output_tokens": max_tokens,
            }
            if system:
                config_kwargs["system_instruction"] = system
            if json_output:
                config_kwargs["response_mime_type"] = "application/json"

            config = types.GenerateContentConfig(**config_kwargs)

            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=config,
                )
                text = (response.text or "").strip()
                if text:
                    return text
            except Exception as exc:
                err_str = str(exc).lower()
                if "404" in err_str or "not_found" in err_str or "not found" in err_str:
                    logger.warning("Gemini model %s returned 404/not found. Checking available models...", model_name)
                    alt_model = _discover_fallback_gemini_model(client)
                    if alt_model and alt_model != model_name:
                        _set_active_gemini_model(alt_model)
                        response = client.models.generate_content(
                            model=alt_model,
                            contents=prompt,
                            config=config,
                        )
                        text = (response.text or "").strip()
                        if text:
                            return text
                raise
        except Exception as exc:
            gemini_error = exc
            logger.warning("Gemini generation failed: %s", exc)

    if groq_key:
        try:
            groq_text = _generate_with_groq(
                prompt,
                system=system,
                json_output=json_output,
                max_tokens=max_tokens,
            )
            if groq_text:
                return groq_text
        except Exception as groq_exc:
            logger.warning("Groq fallback failed: %s", groq_exc)
            if gemini_error:
                raise AIUnavailableError(
                    f"AI providers failed. Gemini: {gemini_error}; Groq: {groq_exc}"
                ) from groq_exc
            raise AIUnavailableError(f"Groq service error: {groq_exc}") from groq_exc

    if gemini_error:
        raise AIUnavailableError(f"AI service error: {gemini_error}") from gemini_error

    raise AIUnavailableError("AI service returned an empty response.")


def _real_embed_texts(texts: list[str]) -> list[list[float]]:
    import sys
    ai_mod = sys.modules.get("app.services.ai")
    if ai_mod and getattr(ai_mod, "embed_texts", None) is not _real_embed_texts:
        return ai_mod.embed_texts(texts)

    if not texts:
        return []

    gemini_key = _get_config("GEMINI_API_KEY")
    if not gemini_key:
        raise AIUnavailableError("GEMINI_API_KEY is not configured for embeddings.")

    try:
        client = _get_gemini_client(gemini_key)
        embed_model = get_embedding_model_name()

        from google.genai import types
        config = types.EmbedContentConfig(output_dimensionality=768)

        response = client.models.embed_content(
            model=embed_model,
            contents=texts,
            config=config,
        )
        if hasattr(response, "embeddings") and response.embeddings:
            return [e.values for e in response.embeddings]
        raise ValueError("Invalid embedding response from Gemini.")
    except Exception as exc:
        logger.warning("Gemini embedding failed: %s", exc)
        raise AIUnavailableError(f"Gemini embedding failed: {exc}") from exc


generate_text = _real_generate_text
embed_texts = _real_embed_texts
