from __future__ import annotations

import json
import logging
import time
from typing import Any, Optional, Type

from openai import OpenAI
from openai import OpenAIError
from pydantic import BaseModel, ValidationError

from ..core.config import settings
from ..core.observability import log_event

logger = logging.getLogger("nourishai.llm")


class LLMService:
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        timeout_seconds: Optional[float] = None,
        client: Optional[OpenAI] = None,
    ) -> None:
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_MODEL
        self.temperature = temperature if temperature is not None else settings.OPENAI_TEMPERATURE
        self.max_tokens = max_tokens if max_tokens is not None else settings.OPENAI_MAX_TOKENS
        self.timeout_seconds = timeout_seconds if timeout_seconds is not None else settings.OPENAI_TIMEOUT_SEC

        if not self.api_key:
            logger.error("OPENAI_API_KEY is not set. LLM features are disabled.")
            self._client: Optional[OpenAI] = None
        else:
            self._client = client or OpenAI(api_key=self.api_key, timeout=self.timeout_seconds)

    def is_configured(self) -> bool:
        return self._client is not None

    def generate_structured(self, system_prompt: str, user_prompt: str, schema_model: Type[BaseModel]) -> BaseModel:
        if self._client is None:
            raise RuntimeError("OpenAI API key is missing. Set OPENAI_API_KEY to enable LLM features.")

        schema = schema_model.model_json_schema()
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": schema_model.__name__,
                "schema": schema,
                "strict": True,
            },
        }

        start = time.perf_counter()
        success = False
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format=response_format,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            success = True
        except OpenAIError as exc:
            log_event(
                logger,
                "llm_error",
                model=self.model,
                error=str(exc),
            )
            raise RuntimeError("OpenAI request failed") from exc
        finally:
            latency_ms = (time.perf_counter() - start) * 1000.0
            log_event(
                logger,
                "llm_call",
                model=self.model,
                schema=schema_model.__name__,
                success=success,
                latency_ms=round(latency_ms, 2),
            )

        content = response.choices[0].message.content if response.choices else None
        if not content:
            raise RuntimeError("OpenAI response was empty")

        try:
            payload: Any = json.loads(content)
        except json.JSONDecodeError as exc:
            log_event(logger, "llm_invalid_json", error=str(exc))
            raise RuntimeError("OpenAI response was not valid JSON") from exc

        try:
            parsed = schema_model.model_validate(payload)
        except ValidationError as exc:
            log_event(logger, "llm_schema_validation_failed", error=str(exc))
            raise RuntimeError("OpenAI response failed schema validation") from exc

        log_event(logger, "llm_response_validated", schema=schema_model.__name__)
        return parsed
