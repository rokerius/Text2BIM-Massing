import json

import pytest

httpx = pytest.importorskip("httpx")
openai = pytest.importorskip("openai")

from text2bim_massing.llm import LLMConfig, OpenAIClient  # noqa: E402


def completion(content="generated code"):
    return {
        "id": "test-completion",
        "object": "chat.completion",
        "created": 0,
        "model": "test-model",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 11, "completion_tokens": 7, "total_tokens": 18},
    }


@pytest.mark.parametrize("configured", [False, True])
def test_real_sdk_request_parameters_and_usage(configured):
    requests = []

    def handle(request):
        requests.append(request)
        return httpx.Response(200, json=completion())

    with openai.OpenAI(
        api_key="test-only",
        base_url="https://test.invalid/v1",
        max_retries=0,
        http_client=httpx.Client(transport=httpx.MockTransport(handle)),
    ) as sdk:
        config = LLMConfig(
            model="test-model",
            temperature=0 if configured else None,
            send_stop=configured,
            reasoning_effort="high" if configured else None,
        )
        client = OpenAIClient(config, client=sdk)
        assert client.generate_one("task", stop=["User:"]) == "generated code"
        body = json.loads(requests[0].content)
        assert str(requests[0].url) == "https://test.invalid/v1/chat/completions"
        assert body["messages"] == [{"role": "user", "content": "task"}]
        if configured:
            assert body["temperature"] == 0
            assert body["stop"] == ["User:"]
            assert body["reasoning_effort"] == "high"
        else:
            assert not {"temperature", "stop", "reasoning_effort"} & body.keys()
        assert client.calls == 1
        assert client.last_response.total_tokens == 18
        assert client.last_response.prompt_tokens == 11
        assert client.last_response.completion_tokens == 7


def test_errors_are_counted_without_stale_success():
    replies = [
        httpx.Response(200, json=completion()),
        httpx.Response(429, json={"error": {"message": "limited"}}),
    ]
    with openai.OpenAI(
        api_key="test-only",
        max_retries=0,
        http_client=httpx.Client(transport=httpx.MockTransport(lambda request: replies.pop(0))),
    ) as sdk:
        client = OpenAIClient(LLMConfig(model="test-model"), client=sdk)
        client.generate_one("first")
        with pytest.raises(openai.RateLimitError):
            client.generate_one("second")
        assert client.calls == 2
        assert client.last_response is None
        assert len(client.responses) == 1


def test_missing_key_fails_without_a_request(monkeypatch):
    monkeypatch.delenv("TEXT2BIM_TEST_KEY", raising=False)
    with pytest.raises(ValueError, match="TEXT2BIM_TEST_KEY"):
        OpenAIClient(LLMConfig(model="test", api_key_env="TEXT2BIM_TEST_KEY"))


@pytest.mark.parametrize(
    "kwargs", [{"model": ""}, {"model": "test", "timeout": 0}, {"model": "test", "max_retries": -1}]
)
def test_invalid_client_configuration(kwargs):
    with pytest.raises(ValueError):
        LLMConfig(**kwargs)


def test_native_function_call_response_and_explicit_remaining_timeout():
    payload = completion(None)
    payload["choices"][0]["message"]["tool_calls"] = [
        {
            "id": "call-architect",
            "type": "function",
            "function": {"name": "plan_designer", "arguments": '{"query":"plan"}'},
        }
    ]
    observed = []

    def handle(request):
        observed.append(request)
        return httpx.Response(200, json=payload)

    with openai.OpenAI(
        api_key="test-only",
        max_retries=3,
        http_client=httpx.Client(transport=httpx.MockTransport(handle)),
    ) as sdk:
        client = OpenAIClient(LLMConfig(model="test"), client=sdk)
        response = client.complete(
            [{"role": "user", "content": "plan"}],
            tools=[
                {
                    "type": "function",
                    "function": {"name": "plan_designer", "parameters": {"type": "object"}},
                }
            ],
            timeout=1.25,
        )
        assert response.tool_calls[0].name == "plan_designer"
        assert response.tool_calls[0].arguments == '{"query":"plan"}'
        assert response.text == ""
        assert "parallel_tool_calls" not in json.loads(observed[0].content)
        assert observed[0].extensions["timeout"]["read"] == 1.25
