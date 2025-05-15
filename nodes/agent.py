from state import State

def MakeAgent(llm_with_tools):
    def agent_function(state: State):
        message = llm_with_tools.invoke(state["messages"])
        # Because we will be interrupting during tool execution,
        # we disable parallel tool calling to avoid repeating any
        # tool invocations when we resume.
        
        assert len(message.tool_calls) <= 1
        return {"messages": [message]}
    
    return agent_function