import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph


conn = sqlite3.connect("/Users/ivanamato/docker_containers/langagency/data/checkpoints.sqlite", check_same_thread=False)
checkpointer = SqliteSaver(conn)