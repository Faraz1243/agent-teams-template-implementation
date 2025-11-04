# Hierarhical Agent Teams Template
## LangGraph Langchain

Just Clone and start writing subagents and tools

Transferred most of the config code to the base agent class to minimise code rewritting and better understandability.

### FUTURE Tasks
Try using cloud sql or redis checkpointer instead of the sqlite checkpointer that stores context localy to prevent context loss due to containerization

### Info
History subagent is working fine. But the maths one isnt. I guess we need to change datatype of float to string in ArgSchema or Input model. And then we can type cast
that to float for calculation

### Problems
Concurrent SQLite writes  ⚠️ Rarely  Could happen with heavy concurrent writes
Solution: Use PostgreSql for checkpointer instead of Sqlite