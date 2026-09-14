def merge_clarification(state):

    original_input = state.get(
        "user_input",
        ""
    )

    clarification = state.get(
        "user_clarification",
        ""
    )

    return {
        "user_input":
            f"{original_input}\n\n{clarification}",
        "clarification_attempts":
            state.get(
                "clarification_attempts",
                0
            ) + 1
    }