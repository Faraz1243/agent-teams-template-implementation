from .tools import *
from langchain.tools import StructuredTool
from .input_models import *

get_sum_tool = StructuredTool(
    name = "get_sum_tool",
    description ="Use this tool to get the sum of two numbers. ",
    coroutine = get_sum_tool,
    args_schema = SumInput,
)

toolbox = [get_sum_tool]