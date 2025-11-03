from agents import BaseAgent, MathsAgent, HistoryAgent

mathsAgent = MathsAgent()
historyAgent = HistoryAgent()


with open("./SupervisorPrompt.txt", "r") as f:
    supervisor_prompt = f.read()

orchestrator = BaseAgent(
    name="main",
    SystemMessage=supervisor_prompt,
    agentsbox=[mathsAgent, historyAgent]  # Pass subagents here
)






# from agents import BaseAgent, MathsAgent, HistoryAgent

# class SuperViserAgent(BaseAgent):
#     def __init__(self):
#         with open("SupervisorPrompt.txt", "r") as file:
#             prompt = file.read()

        
#         super().__init__("SuperViserAgent", prompt, [], [MathsAgent(), HistoryAgent()])  # yaha se shuru karna
#         self.maths_agent = MathsAgent()
#         self.history_agent = HistoryAgent()
