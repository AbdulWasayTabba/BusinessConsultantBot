from langgraph.types import interrupt

from graph.state import BizGPTState


def clarification_node(state: BizGPTState):

    answer = interrupt(
        {
            "question":
                state["clarification_question"],

            "missing_fields":
                state["missing_fields"]
        }
    )

    return {
        "user_clarification": answer
    }