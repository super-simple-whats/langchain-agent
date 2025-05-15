from dotenv import load_dotenv
load_dotenv()

import os
import pyfiglet
from langgraph.graph import StateGraph, START, END
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import ToolNode, tools_condition
from checkpointers.sqlite3 import checkpointer
from hookserver.server import WebhookServer, WebhookResponse
from langgraph.graph.message import add_messages
from nodes.agent import MakeAgent
from tools.search import SearchTool
from tools.whatsapp import SendWhatsapp
from state import State


if __name__ == "__main__":
    print("\n\n")
    print("\033[1m")
    ascii_banner = pyfiglet.figlet_format("SSW Agent Chatbot")
    print(ascii_banner)
    print("\033[0m")
    print("\033[1m=================\033[0m")
    print("\n\n")
    
    #check all the required environment variables
    required_env_vars = [
        "ANTHROPIC_API_KEY",
        "DEVICE_NAME",
        "SSW_API_KEY",
        "MODEL_NAME",
        "HOOKS_PATH",
        "HOOKS_PORT",
        "TAVILY_API_KEY",
    ]
    
    for var in required_env_vars:
        if os.environ.get(var) is None:
            print(f"Error: Environment variable {var} is not set.")
            exit(1)
            
        
    graph_builder = StateGraph(State)
    tools = [SearchTool, SendWhatsapp]
    tool_node = ToolNode(tools=tools)
    
    llm = ChatAnthropic(
        model=os.environ.get("MODEL_NAME"),
        api_key=os.environ.get("ANTHROPIC_API_KEY"),
        )
    
    llm_with_tools = llm.bind_tools(tools)

    agent = MakeAgent(llm_with_tools)

    graph_builder.add_conditional_edges("agent", tools_condition)

    graph_builder.add_node("tools", tool_node)
    graph_builder.add_node("agent", agent)

    graph_builder.add_edge(START, "agent")
    graph_builder.add_edge("tools", "agent")
    graph_builder.add_edge("agent", END)

    graph = graph_builder.compile(checkpointer=checkpointer)
    
    wh_server = WebhookServer()
    
    def stream_graph_updates(thread_id: str, user_input: str):
        try:
            stream_input = {"messages": [{"role": "user", "content": user_input}]}
            config={"configurable": {"thread_id": thread_id}}
            
            events = graph.stream(stream_input, config)
            
            for event in events:
                for value in event.values():
                    # Only send assistant messages to WhatsApp
                    for message in value["messages"]:
                        # Check if message.content is a string
                        if isinstance(message.content, str) and message.type != "tool":
                            SendWhatsapp.func(recipient=thread_id, message=message.content)
                        # Check if message.content is a list with elements containing 'text'
                        elif isinstance(message.content, list) and len(message.content) > 0 and isinstance(message.content[0], dict) and 'text' in message.content[0]:
                            SendWhatsapp.func(recipient=thread_id, message=message.content[0]['text'])
                        elif message.type == "tool":
                            print("Message content is a tool message:", message.content)
                            continue
                        else:
                            print("Message content is not a string:", message.content)
                            continue
        except Exception as e:
            print(f"Error in stream_graph_updates: {e}")
            # Send error message to user
            error_msg = "I'm sorry, I need a moment to think."
            SendWhatsapp.func(recipient=thread_id, message=error_msg)
                    
    def initial_state():
        graph.update_state(
            config={"configurable": {"thread_id": "initial"}},
            values={
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a helpful assistant. Answer the user's questions as accurately and concisely as possible."
                        ),
                    }
                ]
            }
        )
    
    def reset_thread(thread_id: str):
        """
        Resets the conversation state for a specific thread ID.
        This will clear the conversation history and start fresh.
        """
        try:
            cursor = graph.checkpointer.conn.cursor()
            cursor.execute("DELETE FROM checkpoints WHERE thread_id = ?", (thread_id,))
            cursor.execute("DELETE FROM checkpoint_writes WHERE thread_id = ?", (thread_id,))
            cursor.execute("DELETE FROM checkpoint_blobs WHERE thread_id = ?", (thread_id,))
            graph.checkpointer.conn.commit()
            print(f"Thread {thread_id} has been reset successfully")
            initial_state()
            return True
        except Exception as e:
            print(f"Error resetting thread {thread_id}: {e}")
            return False
    
    def webhook_callback(data):
        if data.get("event_name") != "message_received":
            return WebhookResponse(
                data={"status": "error", "message": "Webhook received"},
                code=200
            )
        
        thread_id = data.get("data").get("conversation_id")
        user_input = data.get("data").get("message")
        
        # Check if this is a reset command
        if user_input.lower() == "/reset" or user_input.lower() == "reset":
            reset_thread(thread_id)
            SendWhatsapp.func(recipient=thread_id, message="Ok, let's start again.")
        else:
            stream_graph_updates(thread_id, user_input)
        
        return WebhookResponse(
            data={"status": "success", "message": "Webhook processed successfully"},
            code=200
        )
        
    initial_state()
    
    print(f"Webhook server running on port {os.environ.get('HOOKS_PORT')} and path {os.environ.get('HOOKS_PATH')}")
    print(f"ATTENTION: Don't forget to set up the NGROK tunnel - ngrok http {os.environ.get('HOOKS_PORT')}")
    print(f"and set the webhook URL in your SSW device.")
    print("\n\n")
    wh_server.run(webhook_callback)
    