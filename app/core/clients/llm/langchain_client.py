from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from app.configs.config import settings

LLM_MODEL_NAME = settings.llm_model_name
LLM_MODEL_PROVIDER = settings.llm_model_provider

class LangChainClient:

    def __init__(self, model_name: str, model_provider: str, api_key: str):
        self.model = init_chat_model(
            model=model_name,
            model_provider=model_provider,
            api_key=api_key
        )

    async def run_prompt(self, prompt_template, variables: dict):
        prompt = prompt_template.format_messages(**variables)
        response = await self.model.ainvoke(prompt)
        return response.content