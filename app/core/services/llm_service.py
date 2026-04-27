class LLMService:

    def __init__(self, llm_client):
        self.llm_client = llm_client

    # async def analyze_process(self, process_state: dict):
        # response = await self.llm_client.run_prompt( ... )

        # return self._parse_response(response)

    # def _parse_response(self, text: str):
    #     # convert LLM output -> structured decision
    #     return {
    #         "action": "complete_task",
    #         "confidence": 0.8
    #     }