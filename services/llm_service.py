# ─────────────────────────────────────────────
# services/llm_service.py
#
# Purpose : LLM service via Ollama (chat model)
# ─────────────────────────────────────────────

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from pydantic import BaseModel
from typing import Type, TypeVar, cast

T = TypeVar("T", bound=BaseModel)
from config import AGENT_TEMPERATURE, OLLAMA_BASE_URL, OLLAMA_MODEL


# ─────────────────────────────────────────────
# LLM SERVICE
# ─────────────────────────────────────────────

class LLMService:

    def __init__(self):
        self.llm = ChatOllama(model=OLLAMA_MODEL, 
                            base_url=OLLAMA_BASE_URL,
                            temperature=AGENT_TEMPERATURE)  # type: ignore[call-arg]

    # ── Plain text generation ──
    def generate(self, prompt) -> str:
        messages = [HumanMessage(content=prompt)] if isinstance(prompt, str) else prompt
        return str(self.llm.invoke(messages).content)

    # ── Structured Pydantic output via with_structured_output ──
    def generate_structured(self, prompt, output_schema: Type[T]) -> T:
        messages = [HumanMessage(content=prompt)] if isinstance(prompt, str) else prompt
        return cast(T, self.llm.with_structured_output(output_schema).invoke(messages))


# ─────────────────────────────────────────────
# SINGLETON
# ─────────────────────────────────────────────

llm_service = LLMService()


# ─────────────────────────────────────────────
# LOCAL TEST
# ─────────────────────────────────────────────

if __name__ == "__main__":
    result = llm_service.generate("What is the geopolitical significance of India?")
    print("\nLLM Response:\n", result)
