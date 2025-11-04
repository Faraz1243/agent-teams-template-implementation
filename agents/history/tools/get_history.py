from langchain_core.runnables import RunnableConfig
from utils.utils import log_with_config

@log_with_config
async def get_history_tool(
    country: str = "Utopia",
    config: RunnableConfig = None, 
) -> float:
    print("\033[91m====[Tool HIT] Get History Tool Invoked.====\033[0m")
    print(f"Input: {country}")
    return "helloooo {country}"