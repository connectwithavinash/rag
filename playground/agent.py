from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langchain.chat_models  import init_chat_model
from langchain_tavily import TavilySearch
import os




#search tool
tool = TavilySearch(max_results=2)
tools = [tool]
# tool_response = tool.invoke("What's a 'node' in LangGraph?")
# print(tool_response)


llm = init_chat_model(
    "azure_openai:gpt-4.1",
    azure_deployment="gpt-4.1"
)

#adding the tool to the llm
llm_with_tools = llm.bind_tools(tools)

class State(TypedDict):
    messages: Annotated[list[dict], add_messages]


def chatbot(state: State)-> State:
    return {"messages": [llm_with_tools.invoke(state['messages'])]}


graph_builder = StateGraph(State)

graph_builder.add_node("chatbot",chatbot)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()


def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)


while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        stream_graph_updates(user_input)
    except:
        # fallback if input() is not available
        user_input = "What do you know about LangGraph?"
        print("User: " + user_input)
        stream_graph_updates(user_input)
        break


