from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver

from langchain_groq import ChatGroq

load_dotenv()


llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)


from chatbot.tools import (
    search_study_material,
    calculator
)


tools = [
    search_study_material,
    calculator
]


llm_with_tools = llm.bind_tools(tools)

from langchain_core.messages import SystemMessage


SYSTEM_PROMPT = """
You are StudyMate AI, an AI study assistant.

Your job is to help college students understand
technical subjects.

Rules:

1. Be clear and beginner-friendly.
2. Use the search_study_material tool when the
   question relates to the user's study material.
3. Use the calculator when mathematical calculation
   is required.
4. Do not invent information from the PDF.
5. If the study material does not contain the answer,
   clearly say so.
6. Give examples whenever useful.
7. For programming questions, explain the logic
   before giving code.
"""


def chatbot_node(state):

    messages = state["messages"]

    messages_with_system = [
        SystemMessage(content=SYSTEM_PROMPT)
    ] + messages

    response = llm_with_tools.invoke(
        messages_with_system
    )

    return {
        "messages": [response]
    }

from langgraph.graph import (
    StateGraph,
    START,
    END
)

from langgraph.prebuilt import (
    ToolNode,
    tools_condition
)

from chatbot.state import ChatState

tool_node = ToolNode(tools)

builder = StateGraph(ChatState)

builder.add_node(
    "chatbot",
    chatbot_node
)

builder.add_node(
    "tools",
    tool_node
)
builder.add_edge(
    START,
    "chatbot"
)
builder.add_conditional_edges(
    "chatbot",
    tools_condition
)
builder.add_edge(
    "tools",
    "chatbot"
)
builder.add_edge(
    "chatbot",
    END
)
graph = builder.compile()

memory = MemorySaver()

graph = builder.compile(
    checkpointer=memory
)
config = {
    "configurable": {
        "thread_id": "student-1"
    }
}
