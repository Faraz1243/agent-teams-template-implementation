from .tools import *
from langchain.tools import StructuredTool
from .input_models import *

get_history_tool = StructuredTool(
    name = "get_history_tool",
    description ="Use this tool to get history of anything ",
    coroutine = get_history_tool,
    args_schema = HistoryInput,
)

toolbox = [get_history_tool]