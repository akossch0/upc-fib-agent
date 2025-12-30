"""
Custom ChatLlamaCpp wrapper with proper tool calling support for Qwen models.

This module provides a LangChain-compatible chat model that uses llama-cpp-python
and implements tool calling via Qwen's XML-based format.
"""

import json
import re
from collections.abc import Iterator, Sequence
from typing import Any, Optional

from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models import BaseChatModel, LanguageModelInput
from langchain_core.messages import AIMessage, AIMessageChunk, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool
from langchain_core.utils.function_calling import convert_to_openai_tool
from pydantic import Field, model_validator

TOOL_SYSTEM_PROMPT_TEMPLATE = """{system_prompt}

# Tools

You may call one or more functions to assist with the user query.

You are provided with function signatures within <tools></tools> XML tags:
<tools>
{tools_json}
</tools>

For each function call, return a json object with function name and arguments within <tool_call></tool_call> XML tags:
<tool_call>
{{"name": <function-name>, "arguments": <args-json-object>}}
</tool_call>"""


class ChatLlamaCppTools(BaseChatModel):
    """Chat model using llama-cpp-python with Qwen-style tool calling support."""

    client: Any = None
    model_path: str
    n_ctx: int = 4096
    n_gpu_layers: int = -1
    max_tokens: int = 1024
    temperature: float = 0.7
    top_p: float = 0.95
    verbose: bool = False
    tools: list[dict] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_environment(self) -> "ChatLlamaCppTools":
        if self.client is not None:
            return self

        try:
            from llama_cpp import Llama
        except ImportError as e:
            raise ImportError("llama-cpp-python is required. Install with: pip install llama-cpp-python") from e

        self.client = Llama(
            model_path=self.model_path,
            n_ctx=self.n_ctx,
            n_gpu_layers=self.n_gpu_layers,
            verbose=self.verbose,
        )
        return self

    def close(self) -> None:
        """Release model resources."""
        if self.client is not None:
            del self.client
            self.client = None

    @property
    def _llm_type(self) -> str:
        return "llama-cpp-tools"

    @property
    def _identifying_params(self) -> dict:
        return {
            "model_path": self.model_path,
            "n_ctx": self.n_ctx,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }

    def bind_tools(
        self,
        tools: Sequence[BaseTool | dict],
        **kwargs: Any,
    ) -> Runnable[LanguageModelInput, BaseMessage]:
        formatted_tools = [convert_to_openai_tool(tool) if not isinstance(tool, dict) else tool for tool in tools]
        return self.__class__(
            model_path=self.model_path,
            n_ctx=self.n_ctx,
            n_gpu_layers=self.n_gpu_layers,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            top_p=self.top_p,
            verbose=self.verbose,
            tools=formatted_tools,
            client=self.client,
        )

    def _format_messages(self, messages: list[BaseMessage]) -> list[dict]:
        formatted = []
        system_content = ""

        for msg in messages:
            if isinstance(msg, SystemMessage):
                system_content = msg.content
            elif isinstance(msg, HumanMessage):
                formatted.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                content = msg.content or ""
                if msg.tool_calls:
                    tool_calls_xml = ""
                    for tc in msg.tool_calls:
                        tool_calls_xml += f'\n<tool_call>\n{{"name": "{tc["name"]}", "arguments": {json.dumps(tc["args"])}}}\n</tool_call>'
                    content = content + tool_calls_xml if content else tool_calls_xml.strip()
                formatted.append({"role": "assistant", "content": content})
            elif isinstance(msg, ToolMessage):
                formatted.append({"role": "user", "content": f"<tool_response>\n{msg.content}\n</tool_response>"})

        if self.tools:
            tools_json = "\n".join(json.dumps(tool) for tool in self.tools)
            system_with_tools = TOOL_SYSTEM_PROMPT_TEMPLATE.format(
                system_prompt=system_content or "You are a helpful assistant.",
                tools_json=tools_json,
            )
            formatted.insert(0, {"role": "system", "content": system_with_tools})
        elif system_content:
            formatted.insert(0, {"role": "system", "content": system_content})

        return formatted

    def _parse_tool_calls(self, content: str) -> tuple[str, list[dict]]:
        tool_calls = []
        pattern = r"<tool_call>\s*(\{.*?\})\s*</tool_call>"
        matches = re.findall(pattern, content, re.DOTALL)

        for i, match in enumerate(matches):
            try:
                parsed = json.loads(match)
                tool_calls.append(
                    {
                        "id": f"call_{i}",
                        "name": parsed.get("name", ""),
                        "args": parsed.get("arguments", {}),
                    }
                )
            except json.JSONDecodeError:
                continue

        cleaned_content = re.sub(pattern, "", content, flags=re.DOTALL).strip()
        return cleaned_content, tool_calls

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: Optional[list[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        formatted_messages = self._format_messages(messages)

        response = self.client.create_chat_completion(
            messages=formatted_messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            top_p=self.top_p,
            stop=stop,
        )

        content = response["choices"][0]["message"]["content"] or ""
        cleaned_content, tool_calls = self._parse_tool_calls(content)

        message = AIMessage(
            content=cleaned_content,
            tool_calls=tool_calls if tool_calls else [],
        )

        return ChatResult(generations=[ChatGeneration(message=message)])

    def _stream(
        self,
        messages: list[BaseMessage],
        stop: Optional[list[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        formatted_messages = self._format_messages(messages)

        response = self.client.create_chat_completion(
            messages=formatted_messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            top_p=self.top_p,
            stop=stop,
            stream=True,
        )

        full_content = ""
        for chunk in response:
            if chunk["choices"] and chunk["choices"][0]["delta"].get("content"):
                delta = chunk["choices"][0]["delta"]["content"]
                full_content += delta
                yield ChatGenerationChunk(message=AIMessageChunk(content=delta))

        _, tool_calls = self._parse_tool_calls(full_content)
        if tool_calls:
            yield ChatGenerationChunk(message=AIMessageChunk(content="", tool_calls=tool_calls))
