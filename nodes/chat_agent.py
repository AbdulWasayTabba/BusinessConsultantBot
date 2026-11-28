from config import get_llm
from graph.state import BizGPTState

llm = get_llm(temperature=0)


def chat_agent(state: BizGPTState) -> dict:
    response = llm.invoke(
        f"""
        You are BizGPT.

        Respond naturally and helpfully.

        User:
        {state.get("user_input", "")}
        """
    )

    return {"final_report": response.content}
