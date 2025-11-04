from agents.base_agent import BaseAgent
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

with open("./agents/maths/SystemPrompt.txt", "r") as f:
    system_message_content = f.read()

mathsAgent = BaseAgent("MathsAgent", system_message_content, toolbox=toolbox)