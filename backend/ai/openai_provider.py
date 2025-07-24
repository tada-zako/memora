from openai import AsyncOpenAI
from dataclasses import dataclass
from openai.types.chat import ChatCompletion


@dataclass
class LLMResponse:
    completion_text: str
    raw_response: ChatCompletion


class ProviderOpenAI:
    def __init__(self, api_key: str, model: str, base_url: str | None = None):
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        self.model = model

    async def text_chat(
        self,
        prompt: str,
        images: list[str],  # base64
        context: list | None = None,
        system_prompt: str | None = None,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ):
        model = model or self.model
        context = context or []

        query = {"role": "user", "content": [{"type": "text", "content": prompt}]}
        if images:
            query["content"].extend(
                [{"type": "image_url", "image_url": {"url": img}} for img in images]
            )

        query = [*context, query]
        if system_prompt:
            query.insert(0, {"role": "system", "content": system_prompt})
        resp = await self.client.chat.completions.create(
            model=model,
            messages=query,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        content = resp.choices[0].message.content
        if not content:
            raise ValueError("No content returned from OpenAI API")

        return LLMResponse(
            completion_text=content.strip(),
            raw_response=resp,
        )
