import uuid
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

import streamlit as st
from dotenv import load_dotenv
from langgraph.types import Command

from graph.graph import workflow

load_dotenv()


# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="BizGPT",
    page_icon="📊",
    layout="wide",
)

st.title("📊 BizGPT")
st.caption("AI Business Consulting Agent")


# ==========================================================
# NODE DISPLAY NAMES
# ==========================================================

DISPLAY_NAMES = {
    "intent_router": "Intent Analysis",
    "business_profiler": "Business Profiling",
    "missing_info": "Information Validation",
    "clarification_node": "Requesting Clarification",
    "merge_clarification": "Processing Clarification",
    "diagnosis_agent": "Root Cause Analysis",
    "problem_classifier": "Problem Classification",
    "planner": "Research Planning",
    "dynamic_agent_selection": "Agent Selection",
    "market_agent": "Market Research",
    "competitor_agent": "Competitor Research",
    "marketing_agent": "Marketing Research",
    "operations_agent": "Operations Analysis",
    "finance_agent": "Financial Analysis",
    "customer_agent": "Customer Analysis",
    "research_synthesizer": "Research Synthesis",
    "consultant_agent": "Consulting Recommendations",
    "judge_agent": "Quality Review",
    "research_gap_analyzer": "Research Gap Analysis",
    "replanning_agent": "Research Replanning",
    "targeted_research": "Targeted Research",
    "recommendation_prioritizer": "Recommendation Prioritization",
    "implementation_planner": "Implementation Planning",
    "risk_change_reviewer": "Risk Assessment",
    "report_generator": "Final Report Generation",
    "chat_agent": "General Chat Response",
}


# ==========================================================
# SESSION STATE
# ==========================================================

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

if "waiting_for_clarification" not in st.session_state:
    st.session_state.waiting_for_clarification = False

if "clarification_question" not in st.session_state:
    st.session_state.clarification_question = ""


# ==========================================================
# LANGGRAPH CONFIG
# ==========================================================

config = {
    "configurable": {
        "thread_id": st.session_state.thread_id
    }
}


# ==========================================================
# INTERRUPT HELPERS
# ==========================================================

def extract_interrupt(update):
    """
    Extract a LangGraph interrupt from a streamed update.

    LangGraph exposes interrupts using the special
    '__interrupt__' key.
    """

    if not isinstance(update, dict):
        return None

    interrupt_data = update.get("__interrupt__")

    if not interrupt_data:
        return None

    if isinstance(interrupt_data, (list, tuple)):

        if len(interrupt_data) == 0:
            return None

        return interrupt_data[0]

    return interrupt_data


def get_interrupt_question(interrupt):
    """
    Extract the question/message stored inside
    a LangGraph interrupt.
    """

    if interrupt is None:
        return None

    value = getattr(
        interrupt,
        "value",
        interrupt
    )

    if isinstance(value, dict):

        question = value.get("question")

        if question:
            return str(question)

        # Fallback if interrupt uses another dictionary structure.
        return str(value)

    return str(value)


# ==========================================================
# FALLBACK: CHECK CURRENT GRAPH STATE
# ==========================================================

def get_pending_interrupt(config):
    """
    Fallback check in case the interrupt was not captured
    directly from the stream.
    """

    try:

        snapshot = workflow.get_state(config)

        if snapshot is None:
            return None

        if not snapshot.tasks:
            return None

        for task in snapshot.tasks:

            if not task.interrupts:
                continue

            interrupt = task.interrupts[0]

            question = get_interrupt_question(
                interrupt
            )

            if question:
                return question

    except Exception:
        return None

    return None


# ==========================================================
# DISPLAY INTERRUPT
# ==========================================================

def handle_clarification(question, response_placeholder):
    """
    Put the application into clarification mode.
    """

    if not question:
        return False

    st.session_state.waiting_for_clarification = True

    st.session_state.clarification_question = question

    message = f"❓ {question}"

    response_placeholder.markdown(message)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": message
        }
    )

    return True


# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:

    st.header("Session")

    st.code(
        st.session_state.thread_id
    )

    if st.button("🔄 New Session"):

        st.session_state.thread_id = str(
            uuid.uuid4()
        )

        st.session_state.messages = []

        st.session_state.waiting_for_clarification = False

        st.session_state.clarification_question = ""

        st.rerun()


# ==========================================================
# CHAT HISTORY
# ==========================================================

for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):

        st.markdown(
            msg["content"]
        )


# ==========================================================
# NORMAL USER INPUT
# ==========================================================

if not st.session_state.waiting_for_clarification:

    prompt = st.chat_input(
        "Describe your business problem..."
    )

    if prompt:

        # --------------------------------------------------
        # SAVE USER MESSAGE
        # --------------------------------------------------

        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt
            }
        )

        with st.chat_message("user"):

            st.markdown(prompt)


        # --------------------------------------------------
        # ASSISTANT
        # --------------------------------------------------

        with st.chat_message("assistant"):

            progress_placeholder = st.empty()

            response_placeholder = st.empty()

            completed_steps = []

            interrupt_question = None


            try:

                # ==================================================
                # START GRAPH
                # ==================================================

                initial_state = {
                    "user_input": prompt,
                    "research_findings": [],
                    "replan_count": 0,
                    "clarification_attempts": 0,
                }


                # ==================================================
                # IMPORTANT:
                #
                # DO NOT BREAK OUT OF workflow.stream()
                # WHEN AN INTERRUPT IS FOUND.
                #
                # We store the interrupt and allow the generator
                # to finish naturally.
                # ==================================================

                for update in workflow.stream(
                    initial_state,
                    config=config,
                    stream_mode="updates"
                ):

                    if not update:
                        continue


                    # --------------------------------------------------
                    # CHECK INTERRUPT
                    # --------------------------------------------------

                    interrupt = extract_interrupt(
                        update
                    )

                    if interrupt is not None:

                        interrupt_question = (
                            get_interrupt_question(
                                interrupt
                            )
                        )

                        # IMPORTANT:
                        # Do NOT use break here.
                        #
                        # Let LangGraph's generator close naturally.
                        #
                        continue


                    # --------------------------------------------------
                    # NORMAL NODE UPDATE
                    # --------------------------------------------------

                    if not isinstance(update, dict):
                        continue

                    keys = list(update.keys())

                    if not keys:
                        continue

                    node_name = keys[0]


                    # Ignore internal LangGraph keys.

                    if node_name.startswith("__"):
                        continue


                    friendly_name = DISPLAY_NAMES.get(
                        node_name,
                        node_name
                    )


                    if friendly_name not in completed_steps:

                        completed_steps.append(
                            friendly_name
                        )


                    progress_placeholder.markdown(
                        "\n".join(
                            f"✅ {step}"
                            for step in completed_steps
                        )
                    )


                # ==================================================
                # FALLBACK INTERRUPT CHECK
                # ==================================================

                if not interrupt_question:

                    interrupt_question = (
                        get_pending_interrupt(
                            config
                        )
                    )


                # ==================================================
                # INTERRUPT FOUND
                # ==================================================

                if interrupt_question:

                    handle_clarification(
                        interrupt_question,
                        response_placeholder
                    )

                    # Rerun ONLY after the stream has completely
                    # finished processing.

                    st.rerun()


                # ==================================================
                # GRAPH COMPLETED
                # ==================================================

                st.session_state.waiting_for_clarification = False

                st.session_state.clarification_question = ""


                # --------------------------------------------------
                # GET FINAL STATE
                # --------------------------------------------------

                snapshot = workflow.get_state(
                    config
                )


                if snapshot is None:

                    response_placeholder.error(
                        "Unable to retrieve the final graph state."
                    )

                    st.stop()


                result = snapshot.values or {}


                # --------------------------------------------------
                # FINAL RESPONSE
                # --------------------------------------------------

                response = (
                    result.get("final_report")
                    or result.get("final_response")
                    or result.get("report")
                    or "No report generated."
                )


                progress_placeholder.empty()


                if isinstance(
                    response,
                    dict
                ):

                    response_placeholder.json(
                        response
                    )

                else:

                    response_placeholder.markdown(
                        str(response)
                    )


                # --------------------------------------------------
                # SAVE ASSISTANT RESPONSE
                # --------------------------------------------------

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": str(response)
                    }
                )


            except GeneratorExit:

                # GeneratorExit should normally not happen because
                # we no longer break out of workflow.stream().
                #
                # If it does happen, check whether a pending
                # interrupt exists before treating it as an error.

                interrupt_question = (
                    get_pending_interrupt(
                        config
                    )
                )


                if interrupt_question:

                    handle_clarification(
                        interrupt_question,
                        response_placeholder
                    )

                    st.rerun()

                else:

                    st.warning(
                        "The graph stream was closed before "
                        "a final response was produced."
                    )


            except Exception as e:

                st.error(
                    f"Error: {type(e).__name__}: {str(e)}"
                )


# ==========================================================
# CLARIFICATION / RESUME FLOW
# ==========================================================

else:

    clarification = st.chat_input(
        st.session_state.clarification_question
    )


    if clarification:

        # --------------------------------------------------
        # SAVE USER CLARIFICATION
        # --------------------------------------------------

        st.session_state.messages.append(
            {
                "role": "user",
                "content": clarification
            }
        )


        with st.chat_message("user"):

            st.markdown(
                clarification
            )


        # --------------------------------------------------
        # ASSISTANT
        # --------------------------------------------------

        with st.chat_message("assistant"):

            progress_placeholder = st.empty()

            response_placeholder = st.empty()

            completed_steps = []

            interrupt_question = None


            try:

                # ==================================================
                # RESUME GRAPH
                # ==================================================

                resume_command = Command(
                    resume=clarification
                )


                # ==================================================
                # IMPORTANT:
                #
                # AGAIN, DO NOT BREAK THE STREAM WHEN AN INTERRUPT
                # IS FOUND.
                # ==================================================

                for update in workflow.stream(
                    resume_command,
                    config=config,
                    stream_mode="updates"
                ):

                    if not update:
                        continue


                    # --------------------------------------------------
                    # CHECK INTERRUPT
                    # --------------------------------------------------

                    interrupt = extract_interrupt(
                        update
                    )

                    if interrupt is not None:

                        interrupt_question = (
                            get_interrupt_question(
                                interrupt
                            )
                        )

                        # IMPORTANT:
                        # No break.
                        #
                        # Allow workflow.stream() to finish naturally.

                        continue


                    # --------------------------------------------------
                    # NORMAL NODE UPDATE
                    # --------------------------------------------------

                    if not isinstance(update, dict):
                        continue

                    keys = list(update.keys())

                    if not keys:
                        continue

                    node_name = keys[0]


                    if node_name.startswith("__"):
                        continue


                    friendly_name = DISPLAY_NAMES.get(
                        node_name,
                        node_name
                    )


                    if friendly_name not in completed_steps:

                        completed_steps.append(
                            friendly_name
                        )


                    progress_placeholder.markdown(
                        "\n".join(
                            f"✅ {step}"
                            for step in completed_steps
                        )
                    )


                # ==================================================
                # FALLBACK INTERRUPT CHECK
                # ==================================================

                if not interrupt_question:

                    interrupt_question = (
                        get_pending_interrupt(
                            config
                        )
                    )


                # ==================================================
                # ANOTHER CLARIFICATION IS REQUIRED
                # ==================================================

                if interrupt_question:

                    handle_clarification(
                        interrupt_question,
                        response_placeholder
                    )

                    # Keep clarification mode active.

                    st.session_state.waiting_for_clarification = True

                    st.rerun()


                # ==================================================
                # NO INTERRUPT
                #
                # THE GRAPH HAS FINISHED.
                #
                # This is where your graph should eventually reach:
                #
                # judge_agent
                #      ↓
                # research_gap_analyzer
                #      ↓
                # judge_router
                #      ↓
                # recommendation_prioritizer
                #      ↓
                # implementation_planner
                #      ↓
                # risk_change_reviewer
                #      ↓
                # report_generator
                #      ↓
                # END
                # ==================================================

                st.session_state.waiting_for_clarification = False

                st.session_state.clarification_question = ""


                # --------------------------------------------------
                # GET FINAL STATE
                # --------------------------------------------------

                snapshot = workflow.get_state(
                    config
                )


                if snapshot is None:

                    response_placeholder.error(
                        "Unable to retrieve the graph state."
                    )

                    st.stop()


                result = snapshot.values or {}


                # --------------------------------------------------
                # FINAL RESPONSE
                # --------------------------------------------------

                response = (
                    result.get("final_report")
                    or result.get("final_response")
                    or result.get("report")
                    or "No report generated."
                )


                progress_placeholder.empty()


                if isinstance(
                    response,
                    dict
                ):

                    response_placeholder.json(
                        response
                    )

                else:

                    response_placeholder.markdown(
                        str(response)
                    )


                # --------------------------------------------------
                # SAVE FINAL RESPONSE
                # --------------------------------------------------

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": str(response)
                    }
                )


            except GeneratorExit:

                # Check whether the graph actually paused at another
                # clarification interrupt.

                interrupt_question = (
                    get_pending_interrupt(
                        config
                    )
                )


                if interrupt_question:

                    handle_clarification(
                        interrupt_question,
                        response_placeholder
                    )

                    st.rerun()

                else:

                    st.warning(
                        "The graph stream was closed before "
                        "a final response was produced."
                    )


            except Exception as e:

                st.error(
                    f"Error: {type(e).__name__}: {str(e)}"
                )


# ==========================================================
# DEBUG STATE
# ==========================================================

try:

    snapshot = workflow.get_state(
        config
    )


    with st.expander("Debug State"):

        if snapshot:

            st.json(
                snapshot.values
            )

            # ----------------------------------------------
            # SHOW CURRENT GRAPH NEXT NODES
            # ----------------------------------------------

            if snapshot.next:

                st.write(
                    "Next nodes:",
                    list(snapshot.next)
                )

            # ----------------------------------------------
            # SHOW PENDING INTERRUPTS
            # ----------------------------------------------

            if snapshot.tasks:

                pending_interrupts = []

                for task in snapshot.tasks:

                    if task.interrupts:

                        for interrupt in task.interrupts:

                            pending_interrupts.append(
                                get_interrupt_question(
                                    interrupt
                                )
                            )

                if pending_interrupts:

                    st.write(
                        "Pending interrupts:",
                        pending_interrupts
                    )


except Exception as e:

    with st.expander("Debug State"):

        st.write(
            f"Debug state unavailable: {type(e).__name__}: {str(e)}"
        )