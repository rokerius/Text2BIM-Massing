"""Transport extracted from Text2BIM OpenAiAgent.

Source: tool_agent/agents.py:805–942 at b71b83d0d6640e7dfe7af3fda17b40fb3cfd70dc.
Copyright (c) 2024 dcy0577. MIT; see _vendor/text2bim/LICENSE.
"""

import os
from dataclasses import dataclass

from .geometry import finite_number


@dataclass(frozen=True)
class LLMConfig:
    model: str
    base_url: str | None = None
    api_key_env: str = "OPENAI_API_KEY"
    timeout: float = 60.0
    max_retries: int = 0
    temperature: float | None = None
    reasoning_effort: str | None = None
    max_completion_tokens: int | None = None
    send_stop: bool = False

    def __post_init__(self):
        if not isinstance(self.model, str) or not self.model.strip():
            raise ValueError("An explicit model name is required")
        if finite_number(self.timeout, "timeout") <= 0:
            raise ValueError("timeout must be positive")
        if (
            isinstance(self.max_retries, bool)
            or not isinstance(self.max_retries, int)
            or self.max_retries < 0
        ):
            raise ValueError("max_retries must be a nonnegative integer")
        if (
            self.temperature is not None
            and not 0 <= finite_number(self.temperature, "temperature") <= 2
        ):
            raise ValueError("temperature must be between 0 and 2")
        if self.max_completion_tokens is not None and (
            isinstance(self.max_completion_tokens, bool)
            or not isinstance(self.max_completion_tokens, int)
            or self.max_completion_tokens < 1
        ):
            raise ValueError("max_completion_tokens must be a positive integer")


@dataclass(frozen=True)
class ToolCall:
    id: str
    name: str
    arguments: str


@dataclass(frozen=True)
class LLMResponse:
    text: str
    model: str
    prompt_tokens: int | None
    completion_tokens: int | None
    total_tokens: int | None
    tool_calls: tuple[ToolCall, ...] = ()


class OpenAIClient:
    """One configurable synchronous client; original generate_one/generate_many interface."""

    def __init__(self, config: LLMConfig, *, api_key: str | None = None, client=None):
        self.config, self.model = config, config.model
        self.calls = 0
        self.last_response: LLMResponse | None = None
        self.responses: list[LLMResponse] = []
        self._owns_client = client is None
        if client is None:
            try:
                from openai import OpenAI
            except ImportError as error:
                raise ImportError("Install text2bim-massing[llm] to use the LLM client") from error
            api_key = api_key or os.environ.get(config.api_key_env)
            if not api_key:
                raise ValueError(f"Set {config.api_key_env} or pass api_key explicitly")
            client = OpenAI(
                api_key=api_key,
                base_url=config.base_url,
                timeout=config.timeout,
                max_retries=config.max_retries,
            )
        self.client = client

    def generate_many(self, prompts, stop=None):
        return [self._chat_generate(prompt, stop) for prompt in prompts]

    def generate_one(self, prompt, stop=None):
        return self._chat_generate(prompt, stop)

    def _chat_generate(self, prompt, stop):
        response = self.complete([{"role": "user", "content": prompt}], stop=stop)
        if response.tool_calls:
            raise ValueError("Unexpected tool call in a text-only completion")
        return response.text

    def complete(self, messages, *, tools=None, stop=None, timeout=None) -> LLMResponse:
        options = {}
        for key in ("temperature", "reasoning_effort", "max_completion_tokens"):
            value = getattr(self.config, key)
            if value is not None:
                options[key] = value
        if self.config.send_stop and stop:
            options["stop"] = stop
        if tools:
            options.update(tools=tools, tool_choice="auto")
        self.calls += 1
        self.last_response = None
        client = self.client
        if timeout is not None:
            # A workflow budget must count every HTTP attempt, including failures.
            client = client.with_options(timeout=min(timeout, self.config.timeout), max_retries=0)
        result = client.chat.completions.create(
            model=self.model,
            messages=messages,
            **options,
        )
        if not result.choices:
            raise ValueError("The model did not return a text completion")
        message = result.choices[0].message
        tool_calls = tuple(
            ToolCall(call.id, call.function.name, call.function.arguments)
            for call in message.tool_calls or ()
        )
        if not isinstance(message.content, str) and not tool_calls:
            raise ValueError("The model did not return a text completion")
        usage = result.usage
        response = LLMResponse(
            text=message.content or "",
            model=result.model,
            prompt_tokens=usage.prompt_tokens if usage else None,
            completion_tokens=usage.completion_tokens if usage else None,
            total_tokens=usage.total_tokens if usage else None,
            tool_calls=tool_calls,
        )
        self.last_response = response
        self.responses.append(response)
        return response

    def close(self):
        if self._owns_client:
            self.client.close()
