from graph.state import BizGPTState
from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="phi3:mini",
    temperature=0
)


def chat_agent(state: BizGPTState):

    response = llm.invoke(
        f"""
        You are BizGPT.

        Respond naturally and helpfully.

        User:
        {state.get("user_input", "")}
        """
    )

    return {
        "final_report": response.content
    }