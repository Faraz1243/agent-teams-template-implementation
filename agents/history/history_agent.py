from agents.base_agent import BaseAgent

from .tools import *
from langchain.tools import StructuredTool
from .input_models import HistoryInput

get_history_tool = StructuredTool(
    name = "get_history_tool",
    description ="Use this tool to get history of anything ",
    coroutine = get_history_tool,
    args_schema = HistoryInput,
)

toolbox = [get_history_tool]
with open("./agents/history/SystemPrompt.txt", "r") as f:
    system_message_content = f.read()
 
historyAgent = BaseAgent("HistoryAgent", "You are History Agent", toolbox=toolbox)