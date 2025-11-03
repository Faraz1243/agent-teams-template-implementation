from .toolbox import toolbox as tools_kit
from agents.base_agent import BaseAgent

class HistoryAgent(BaseAgent):
    def __init__(self):
        with open("./agents/history/SystemPrompt.txt", "r") as f:
            system_message_content = f.read()
        print("histttt" + system_message_content)
        super().__init__("HistoryAgent", system_message_content, toolbox=tools_kit)

    async def async_init(self):
        await super().async_init()
        print(f"{self.name} initialized.")

    async def aclose(self):
        await super().aclose()
        print(f"{self.name} closed.")
 