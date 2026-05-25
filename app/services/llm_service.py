"""LLM Gateway — Groq (primary) + Ollama (fallback) com métodos especializados v2."""
from __future__ import annotations
import json
import logging
import httpx
from abc import ABC, abstractmethod
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import settings
from app.prompts.system_prompt import build_system_prompt

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    @abstractmethod
    async def chat(self, messages: list[dict], system: str, max_tokens: int = 300) -> str: ...


class OpenAICompatibleProvider(LLMProvider):
    """Provider genérico para APIs OpenAI-compatible (xAI, Groq, OpenRouter...)."""

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(min=1, max=3))
    async def chat(self, messages: list[dict], system: str, max_tokens: int = 300) -> str:
        if not settings.llm_api_key:
            raise ValueError("LLM_API_KEY não configurada")

        payload = {
            "model": settings.llm_model,
            "messages": [{"role": "system", "content": system}] + messages,
            "max_tokens": max_tokens,
            "temperature": 0.7,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                settings.llm_base_url,
                json=payload,
                headers={"Authorization": f"Bearer {settings.llm_api_key}"},
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()


class OllamaProvider(LLMProvider):
    """Ollama local — fallback offline."""

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(min=1, max=3))
    async def chat(self, messages: list[dict], system: str, max_tokens: int = 300) -> str:
        payload = {
            "model": settings.ollama_model,
            "messages": [{"role": "system", "content": system}] + messages,
            "stream": False,
            "options": {"num_predict": max_tokens},
        }
        async with httpx.AsyncClient(
            base_url=settings.ollama_base_url, timeout=30.0
        ) as client:
            resp = await client.post("/api/chat", json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["message"]["content"].strip()


class LLMGateway:
    """Circuit breaker com fallback automático Groq → Ollama + métodos especializados."""

    _FAILURE_THRESHOLD = 3

    def __init__(self):
        self.primary = OpenAICompatibleProvider()
        self.fallback = OllamaProvider()
        self._failures = 0
        self._circuit_open = False

    async def chat(self, messages: list[dict], system: str, max_tokens: int = 300) -> str:
        """Chamada genérica ao LLM com fallback automático."""
        if not self._circuit_open:
            try:
                response = await self.primary.chat(messages, system, max_tokens)
                self._failures = 0  # reset em caso de sucesso
                return response
            except Exception as e:
                self._failures += 1
                logger.warning(f"Groq falhou ({self._failures}x): {e}")
                if self._failures >= self._FAILURE_THRESHOLD:
                    self._circuit_open = True
                    logger.error("Circuit breaker aberto — usando Ollama")

        try:
            return await self.fallback.chat(messages, system, max_tokens)
        except Exception as e:
            logger.error(f"Ollama também falhou: {e}")
            return "Eita! Tive um problema técnico aqui. Tenta novamente em uns minutinhos? 😅"

    async def parse_transaction(self, text: str) -> dict:
        """Usa sistema de parsing estrito para extrair transação de texto livre."""
        from app.prompts.parse_prompt import PARSE_SYSTEM_PROMPT
        result = await self.chat(
            messages=[{"role": "user", "content": text}],
            system=PARSE_SYSTEM_PROMPT,
            max_tokens=150,
        )
        # Limpeza defensiva: remove markdown fences se houver
        clean = result.strip()
        if clean.startswith("```"):
            clean = clean.removeprefix("```json").removeprefix("```")
        if clean.endswith("```"):
            clean = clean.removesuffix("```")
        clean = clean.strip()
        try:
            return json.loads(clean)
        except json.JSONDecodeError:
            logger.warning(f"LLM retornou JSON inválido: {result!r}")
            return {"found": False}

    async def qa_answer(
        self,
        question: str,
        history: list[dict] | None = None,
        user_context: dict | object | None = None,
        month_summary: dict | None = None,
    ) -> str:
        """Responde perguntas financeiras usando histórico e contexto do usuário."""
        system = (
            build_system_prompt(user_context, month_summary=month_summary)
            if user_context is not None
            else "Você é o Fini, parceiro de educação financeira de jovens brasileiros. Responda em até 150 palavras."
        )
        messages = (history or []) + [{"role": "user", "content": question}]
        return await self.chat(messages=messages, system=system, max_tokens=300)

    async def generate_insight(self, summary_data: dict | str) -> str:
        """Gera insight contextualizado de 1-2 frases."""
        from app.prompts.insight_prompt import INSIGHT_SYSTEM_PROMPT
        context = (
            json.dumps(summary_data, ensure_ascii=False, default=str)
            if isinstance(summary_data, dict)
            else summary_data
        )
        return await self.chat(
            messages=[{"role": "user", "content": context}],
            system=INSIGHT_SYSTEM_PROMPT,
            max_tokens=100,
        )


# Singleton
llm_gateway = LLMGateway()
