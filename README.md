Transfering most of the config code to the base agent class to minimise code rewritting and better understandability.

Challenge:
Making one checkpointer or memory and get it shared by all the agents instead of separate checkpointer for each agent

FUTURE Tasks:
Try using cloud sql or redis checkpointer instead of the sqlite checkpointer that stores context localy to prevent context loss due to containerization
Pass logs array with config so that we can log each tool call, its parameters and output. Maybe use decorator function for that.


Info: History subagent is working fine. But the maths one isnt. Igues we need to change datatype of float to string in ArgSchema or Input model. And then we can type cast
that to float for calculation