from agents import BaseAgent, mathsAgent, historyAgent

with open("./SupervisorPrompt.txt", "r") as f:
    supervisor_prompt = f.read()

orchestrator = BaseAgent(
    name="RootAgent",
    SystemMessage=supervisor_prompt,
    agentsbox=[mathsAgent, historyAgent]  # Pass subagents here
)

