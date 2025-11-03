from langchain_core.runnables import RunnableConfig

async def get_sum_tool(
    a: float = 0,
    b: float = 0,
    config: RunnableConfig = None, 
) -> float:
    print("\033[91m====[Tool HIT] Get Sumr Tool Invoked.====\033[0m")
    print(f"Input: {a} , {b}")
    return a + b