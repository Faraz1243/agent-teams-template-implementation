# this file is a temp file to turn the chatbot code into a class
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from langgraph.graph import MessagesState, START, StateGraph, END
from langgraph.prebuilt import tools_condition
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig
from abc import ABC
from langchain.tools import StructuredTool
from fastapi.encoders import jsonable_encoder
import datetime
from typing import Literal, List

# SQLITE Saver
DB_FOLDER = "sqlite"
os.makedirs(DB_FOLDER, exist_ok=True)
DB_PATH = os.path.join(DB_FOLDER, "chatbot_memory.sqlite")
# CloudSQL Saver
DB_URL = "postgresql://neondb_owner:npg_vSqeky9BIxF7@ep-cool-king-ad60x9z6-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require"


USE_CLOUDSQL = True  # Set to True to use CloudSQL Postgres saver

load_dotenv()


class BaseAgent(ABC):
    _saver_ctx: AsyncSqliteSaver = None
    memory = None

    def __init__(self, name, SystemMessage, toolbox:list[StructuredTool]=[], agentsbox:list["BaseAgent"]=[]):
        GROK_MODEL = "openai/gpt-oss-120b"
        self.grok_api_key = os.getenv("GROQ_API_KEY")
        self.simple_llm = ChatOpenAI(
            model=GROK_MODEL,
            api_key=self.grok_api_key,
            base_url="https://api.groq.com/openai/v1/"
        )
        self.name = name
        self.toolbox = toolbox  # Regular tools
        self.agentsbox = agentsbox  # List of subagent instances
        
        # Create subagent tool definitions for the LLM
        self.subagent_tools = self._create_subagent_tools()
        
        # Bind both regular tools and subagent tools
        all_tools = self.toolbox + self.subagent_tools
        self.llm_with_tools = self.simple_llm.bind_tools(all_tools)

        # memory will be set later in async init
        self.memory = None
        self.react_graph_with_memory = None
        self.assistant_system_message = BaseAgent.generate_user_context_system_message(SystemMessage)

    def _create_subagent_tools(self) -> List[dict]:
        """Create tool definitions for subagents so the LLM can call them"""
        subagent_tools = []
        
        for agent in self.agentsbox:
            tool_def = {
                "name": f"{agent.name}_agent",
                "description": f"Delegate tasks to the {agent.name} specialized agent. Use this when the task requires specialized expertise from {agent.name}.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task": {
                            "type": ["string", "null"],
                            "description": f"The specific task to delegate to {agent.name}",
                            "default": ""
                        },
                        "context": {
                            "type": "string",
                            "description": "Additional context or information the subagent needs"
                        }
                    },
                    "required": ["task"]
                }
            }
            subagent_tools.append(tool_def)
        
        return subagent_tools

    def _route_after_assistant(self, state: MessagesState) -> Literal["tools", "subagents", "__end__"]:
        """Route the assistant's response to tools, subagents, or end."""
        last_message = state["messages"][-1]
        
        if not isinstance(last_message, AIMessage):
            return "__end__"
        
        if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
            return "__end__"
        
        tool_calls = last_message.tool_calls
        
        # Check if any tool call is for a subagent
        subagent_names = {f"{agent.name}_agent" for agent in self.agentsbox}
        called_tools = {tc["name"] for tc in tool_calls}
        
        if called_tools & subagent_names:  # If intersection exists
            print(f"\033[95m[ROUTER] Routing to subagents: {called_tools & subagent_names}\033[0m")
            return "subagents"
        
        # Regular tool calls
        print(f"\033[94m[ROUTER] Routing to tools: {called_tools}\033[0m")
        return "tools"

    async def async_init(self):
        if BaseAgent._saver_ctx is None:
            if USE_CLOUDSQL:
                BaseAgent._saver_ctx = AsyncPostgresSaver.from_conn_string(DB_URL)
            else:
                BaseAgent._saver_ctx = AsyncSqliteSaver.from_conn_string(DB_PATH)
        if BaseAgent.memory is None:
            BaseAgent.memory = await BaseAgent._saver_ctx.__aenter__()   # manually enter
            if USE_CLOUDSQL:
                await BaseAgent.memory.setup()
        
        # Initialize all subagents
        for agent in self.agentsbox:
            if hasattr(agent, 'async_init'):
                await agent.async_init()
        
        self.react_graph_with_memory = self._build_graph()
        print(f"{self.name} initialized.")

    async def aclose(self):
        # Close all subagents first
        for agent in self.agentsbox:
            if hasattr(agent, 'aclose'):
                await agent.aclose()
        
        
        # Then close this agent's resources
        if BaseAgent._saver_ctx is not None:
            await self._saver_ctx.__aexit__(None, None, None)

    @staticmethod
    def generate_user_context_system_message(prompt) -> SystemMessage:
        system_prompt = f"Date Today: {datetime.datetime.now()}\n\n {prompt}"
        return SystemMessage(content=system_prompt)

    async def assistant(self, state: MessagesState, config: RunnableConfig = None):
        return {
            "messages": [
                await self.llm_with_tools.ainvoke(
                    [self.assistant_system_message] + state["messages"],
                    config=config
                )
            ]
        }

    async def chatbot_with_memory(self, user_request: str, thread_id: str, user_id: str, logs=[]):
        print(f"\033[94m ============= [Agent:{self.name}] ============= \033[0m")
        print(f"\033[94mUser Request: {user_request}\033[0m")
        print(f"\033[94mThread ID: {thread_id}\033[0m")
        print(f"\033[94mUser ID: {user_id}\033[0m")
        
        result = await self.react_graph_with_memory.ainvoke(
            {"messages": [HumanMessage(content=user_request)]},
            config={"configurable": {"thread_id": thread_id, "user_id": user_id, "request_logs": logs}},
        )
        return {
            "thread_id": thread_id,
            "message" : result["messages"][-1].content,
            "logs": jsonable_encoder(logs)
        }
    
    async def tool_node(self, state: MessagesState, config: RunnableConfig = None):
        """Custom tool node that properly passes config to async tools"""
        outputs = []
        
        if not state.get("messages") or not state["messages"]:
            return {"messages": outputs}
        
        last_message = state["messages"][-1]
        if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
            return {"messages": outputs}
        
        # Get subagent names to skip them in tool_node
        subagent_names = {f"{agent.name}_agent" for agent in self.agentsbox}
        
        for tool_call in last_message.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_call_id = tool_call["id"]
            
            # Skip subagent calls (they're handled in subagent_node)
            if tool_name in subagent_names:
                continue
            
            print(f"\033[93m[TOOL] Executing: {tool_name}, Args: {tool_args}\033[0m")
            
            # Find the matching tool
            tool = next((t for t in self.toolbox if t.name == tool_name), None)
            if tool is None:
                outputs.append(
                    ToolMessage(
                        content=f"Error: tool {tool_name} not found",
                        tool_call_id=tool_call_id
                    )
                )
                continue            
            
            try:
                # Invoke the tool with config
                result = await tool.ainvoke(tool_args, config=config)
                    
                print(f"\033[92m[SUCCESS] Tool '{tool_name}' completed\033[0m")
                outputs.append(
                    ToolMessage(
                        content=str(result),
                        tool_call_id=tool_call_id
                    )
                )
            except Exception as e:
                print(f"\033[91m[ERROR] Tool '{tool_name}' execution failed: {str(e)}\033[0m")
                import traceback
                traceback.print_exc()
                
                outputs.append(
                    ToolMessage(
                        content=f"Error: {str(e)}",
                        tool_call_id=tool_call_id
                    )
                )
        
        return {"messages": outputs}

    def _build_graph(self):
        builder = StateGraph(MessagesState)
        
        # Add main nodes - only add methods, not agent instances
        builder.add_node("assistant", self.assistant)
        builder.add_node("tools", self.tool_node)
        
        # Only add subagent node if there are subagents
        if len(self.agentsbox)!=0:
            builder.add_node("subagents", self.subagent_node)

        # Set up routing
        builder.add_edge(START, "assistant")
        
        # Conditional routing from assistant
        if len(self.agentsbox)!=0:
            # If we have subagents, use custom routing
            builder.add_conditional_edges(
                "assistant",
                self._route_after_assistant,
                {
                    "tools": "tools",
                    "subagents": "subagents",
                    "__end__": END
                }
            )
            builder.add_edge("subagents", "assistant")
        else:
            # If no subagents, use standard tools_condition
            builder.add_conditional_edges("assistant", tools_condition)
        
        # Tools always return to assistant
        builder.add_edge("tools", "assistant")

        
        return builder.compile(checkpointer=self.memory)


    async def subagent_node(self, state: MessagesState, config: RunnableConfig = None):
        print(f"\033[95m[SUBAGENT NODE] Invoked subagent node\033[0m")
        """Node that handles subagent delegation"""
        outputs = []
        
        if not state.get("messages") or not state["messages"]:
            return {"messages": outputs}
        
        last_message = state["messages"][-1]
        if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
            return {"messages": outputs}
        
        # Create a lookup for subagents
        subagent_lookup = {f"{agent.name}_agent": agent for agent in self.agentsbox}
        
        for tool_call in last_message.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_call_id = tool_call["id"]
            
            # Only process subagent calls
            if tool_name not in subagent_lookup:
                continue
            
            subagent = subagent_lookup[tool_name]
            task = tool_args.get("task", "")
            context = tool_args.get("context") or ""
            
            print(f"\033[95m[SUBAGENT] Delegating to: {subagent.name}\033[0m")
            print(f"\033[95m[SUBAGENT] Task: {task}\033[0m")
            
            try:
                # Build the request for the subagent
                if context:
                    subagent_request = f"{task}\n\nContext: {context}"
                else:
                    subagent_request = task
                
                # Get the thread_id from config to maintain separate conversation threads
                thread_id = config.get("configurable", {}).get("thread_id", "default")
                user_id = config.get("configurable", {}).get("user_id", "default")
                logs = config.get("configurable", {}).get("request_logs", [])
                subagent_thread_id = f"{thread_id}_subagent_{subagent.name}"
                
                # Invoke the subagent using its chatbot_with_memory method
                result = await subagent.chatbot_with_memory(
                    user_request=subagent_request,
                    thread_id=subagent_thread_id,
                    user_id=user_id,
                    logs=logs
                )
                
                print(f"\033[95m[SUBAGENT] {subagent.name} completed successfully\033[0m")
                print(f"\033[96m[SUBAGENT] Result: {result}\033[0m")
                
                outputs.append(
                    ToolMessage(
                        content=f"Subagent {subagent.name} result:\n{result}",
                        tool_call_id=tool_call_id
                    )
                )
                
            except Exception as e:
                print(f"\033[91m[ERROR] Subagent '{subagent.name}' execution failed: {str(e)}\033[0m")
                import traceback
                traceback.print_exc()
                
                outputs.append(
                    ToolMessage(
                        content=f"Subagent {subagent.name} error: {str(e)}",
                        tool_call_id=tool_call_id
                    )
                )
        
        return {"messages": outputs}
