from graph.state import BizGPTState
from config import get_llm

llm = get_llm(temperature=0)


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