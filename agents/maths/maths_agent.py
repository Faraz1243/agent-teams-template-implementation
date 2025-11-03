from .toolbox import toolbox as tools_kit
from agents.base_agent import BaseAgent



class MathsAgent(BaseAgent):
    def __init__(self):
        with open("./agents/maths/SystemPrompt.txt", "r") as f:
            system_message_content = f.read()
        super().__init__("MathAgent", system_message_content, tools_kit)

    async def async_init(self):
        await super().async_init()
        print(f"{self.name} initialized.")

    async def aclose(self):
        await super().aclose()
        print(f"{self.name} closed.")
 