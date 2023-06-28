from pytest import MonkeyPatch
from typing import Any, Generator
from llama_index.llms.base import ChatMessage
from llama_index.llms.openai import OpenAI


def mock_completion(*args: Any, **kwargs: Any) -> dict:
    # Example taken from https://platform.openai.com/docs/api-reference/completions/create
    return {
        "id": "cmpl-uqkvlQyYK7bGYrRHQ0eXlWi7",
        "object": "text_completion",
        "created": 1589478378,
        "model": "text-davinci-003",
        "choices": [
            {
                "text": "\n\nThis is indeed a test",
                "index": 0,
                "logprobs": None,
                "finish_reason": "length",
            }
        ],
        "usage": {"prompt_tokens": 5, "completion_tokens": 7, "total_tokens": 12},
    }


def mock_chat_completion(*args: Any, **kwargs: Any) -> dict:
    # Example taken from https://platform.openai.com/docs/api-reference/chat/create
    return {
        "id": "chatcmpl-abc123",
        "object": "chat.completion",
        "created": 1677858242,
        "model": "gpt-3.5-turbo-0301",
        "usage": {"prompt_tokens": 13, "completion_tokens": 7, "total_tokens": 20},
        "choices": [
            {
                "message": {"role": "assistant", "content": "\n\nThis is a test!"},
                "finish_reason": "stop",
                "index": 0,
            }
        ],
    }


def mock_completion_stream(*args: Any, **kwargs: Any) -> Generator[dict, None, None]:
    # Example taken from https://github.com/openai/openai-cookbook/blob/main/examples/How_to_stream_completions.ipynb
    responses = [
        {
            "choices": [
                {
                    "text": "1",
                }
            ],
        },
        {
            "choices": [
                {
                    "text": "2",
                }
            ],
        },
    ]
    for response in responses:
        yield response


def mock_chat_completion_stream(
    *args: Any, **kwargs: Any
) -> Generator[dict, None, None]:
    # Example taken from: https://github.com/openai/openai-cookbook/blob/main/examples/How_to_stream_completions.ipynb
    responses = [
        {
            "choices": [
                {"delta": {"role": "assistant"}, "finish_reason": None, "index": 0}
            ],
            "created": 1677825464,
            "id": "chatcmpl-6ptKyqKOGXZT6iQnqiXAH8adNLUzD",
            "model": "gpt-3.5-turbo-0301",
            "object": "chat.completion.chunk",
        },
        {
            "choices": [
                {"delta": {"content": "\n\n"}, "finish_reason": None, "index": 0}
            ],
            "created": 1677825464,
            "id": "chatcmpl-6ptKyqKOGXZT6iQnqiXAH8adNLUzD",
            "model": "gpt-3.5-turbo-0301",
            "object": "chat.completion.chunk",
        },
        {
            "choices": [{"delta": {"content": "2"}, "finish_reason": None, "index": 0}],
            "created": 1677825464,
            "id": "chatcmpl-6ptKyqKOGXZT6iQnqiXAH8adNLUzD",
            "model": "gpt-3.5-turbo-0301",
            "object": "chat.completion.chunk",
        },
        {
            "choices": [{"delta": {}, "finish_reason": "stop", "index": 0}],
            "created": 1677825464,
            "id": "chatcmpl-6ptKyqKOGXZT6iQnqiXAH8adNLUzD",
            "model": "gpt-3.5-turbo-0301",
            "object": "chat.completion.chunk",
        },
    ]
    for response in responses:
        yield response


def test_completion_model_basic(monkeypatch: MonkeyPatch):
    monkeypatch.setattr(
        "llama_index.llms.openai.completion_with_retry", mock_completion
    )

    llm = OpenAI(model="text-davinci-003")
    prompt = "test prompt"
    message = ChatMessage(role="user", content="test message")

    response = llm.complete(prompt)
    assert response.text == "\n\nThis is indeed a test"

    response = llm.chat([message])
    assert response.message.content == "\n\nThis is indeed a test"


def test_chat_model_basic(monkeypatch: MonkeyPatch):
    monkeypatch.setattr(
        "llama_index.llms.openai.completion_with_retry", mock_chat_completion
    )

    llm = OpenAI(model="gpt-3.5-turbo")
    prompt = "test prompt"
    message = ChatMessage(role="user", content="test message")

    response = llm.complete(prompt)
    assert response.text == "\n\nThis is a test!"

    response = llm.chat([message])
    assert response.message.content == "\n\nThis is a test!"


def test_completion_model_streaming(monkeypatch: MonkeyPatch):
    monkeypatch.setattr(
        "llama_index.llms.openai.completion_with_retry", mock_completion_stream
    )

    llm = OpenAI(model="text-davinci-003")
    prompt = "test prompt"
    message = ChatMessage(role="user", content="test message")

    response_gen = llm.stream_complete(prompt)
    responses = list(response_gen)
    assert responses[-1].text == "12"
    response_gen = llm.stream_chat([message])
    responses = list(response_gen)
    assert responses[-1].message.content == "12"


def test_chat_model_streaming(monkeypatch: MonkeyPatch):
    monkeypatch.setattr(
        "llama_index.llms.openai.completion_with_retry", mock_chat_completion_stream
    )

    llm = OpenAI(model="gpt-3.5-turbo")
    prompt = "test prompt"
    message = ChatMessage(role="user", content="test message")

    response_gen = llm.stream_complete(prompt)
    responses = list(response_gen)
    assert responses[-1].text == "\n\n2"

    response_gen = llm.stream_chat([message])
    responses = list(response_gen)
    assert responses[-1].message.content == "\n\n2"
    assert responses[-1].message.role == "assistant"
