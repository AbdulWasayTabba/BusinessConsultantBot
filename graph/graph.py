from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
import pprint

from graph.state import BizGPTState

# Core Nodes
from nodes.merge_clarification import merge_clarification
from nodes.clarification_node import clarification_node
from nodes.missing_info import missing_info
from nodes.intent_router import intent_router
from nodes.business_profiler import business_profiler
from nodes.diagnosis_agent import diagnosis_agent
from nodes.problem_classifier import problem_classifier
from nodes.planner import planner
from nodes.dynamic_agent_selection import dynamic_agent_selection

# Research & Consulting
from nodes.research_synthesizer import research_synthesizer
from nodes.consultant_agent import consultant_agent

# Reflection / Self-RAG
from nodes.judge_agent import judge_agent
from nodes.research_gap_analyzer import research_gap_analyzer
from nodes.replanning_agent import replanning_agent
from nodes.targeted_research import targeted_research

# Output Generation
from nodes.recommendation_prioritizer import recommendation_prioritizer
from nodes.implementation_planner import implementation_planner
from nodes.risk_change_reviewer import risk_change_reviewer
from nodes.report_generator import report_generator

# Research Agents
from agents.market_agent import market_agent
from agents.competitor_agent import competitor_agent
from agents.marketing_agent import marketing_agent
from agents.operations_agent import operations_agent
from agents.finance_agent import finance_agent
from agents.customer_agent import customer_agent

pp = pprint.PrettyPrinter(indent=2)

from nodes.chat_agent import chat_agent
# =========================
# ROUTERS
# =========================

def intent_route(state: BizGPTState):

    route = state.get("route_type")

    if route == "business_analysis":
        return "analysis"

    return "chat"

def route_agents(state: BizGPTState):

    print("\n" + "=" * 60)
    print("DYNAMIC AGENT SELECTION")
    print("=" * 60)

    print("Selected Agents:")
    pp.pprint(state["selected_agents"])

    return [
        Send(agent, state)
        for agent in state["selected_agents"]
    ]


def judge_router(state: BizGPTState):

    print("\n" + "=" * 60)
    print("JUDGE ROUTER")
    print("=" * 60)

    print("Judge Feedback:")
    pp.pprint(state.get("judge_feedback", {}))

    print("\nResearch Gaps:")
    pp.pprint(state.get("research_gaps", {}))

    print("\nReplan Count:")
    print(state.get("replan_count", 0))

    feedback = state.get("judge_feedback", {})
    gaps = state.get("research_gaps", {})

    if (
        feedback.get("research_needed", False)
        and gaps.get("prioritized_gaps")
        and state.get("replan_count", 0) < 1
    ):
        print("\nDECISION: REPLAN\n")
        return "replan"

    print("\nDECISION: CONTINUE\n")
    return "continue"


def missing_info_router(state: BizGPTState):

    missing = state.get("missing_fields", [])

    attempts = state.get(
        "clarification_attempts",
        0
    )

    if missing and attempts < 3:
        return "need_more_info"

    return "continue"



# =========================
# GRAPH
# =========================

graph = StateGraph(BizGPTState)

# Core Nodes
graph.add_node("merge_clarification",merge_clarification)
graph.add_node("missing_info", missing_info)
graph.add_node("clarification_node",clarification_node)
graph.add_node("intent_router", intent_router)
graph.add_node("business_profiler", business_profiler)
graph.add_node("diagnosis_agent", diagnosis_agent)
graph.add_node("problem_classifier", problem_classifier)
graph.add_node("planner", planner)
graph.add_node("dynamic_agent_selection", dynamic_agent_selection)

# Research Agents
graph.add_node("market_agent", market_agent)
graph.add_node("competitor_agent", competitor_agent)
graph.add_node("marketing_agent", marketing_agent)
graph.add_node("operations_agent", operations_agent)
graph.add_node("finance_agent", finance_agent)
graph.add_node("customer_agent", customer_agent)

# Research / Consulting
graph.add_node("research_synthesizer", research_synthesizer)
graph.add_node("consultant_agent", consultant_agent)

# Reflection
graph.add_node("judge_agent", judge_agent)
graph.add_node("research_gap_analyzer", research_gap_analyzer)
graph.add_node("replanning_agent", replanning_agent)
graph.add_node("targeted_research", targeted_research)

graph.add_node(
    "chat_agent",
    chat_agent
)

# Output
graph.add_node(
    "recommendation_prioritizer",
    recommendation_prioritizer
)

graph.add_node(
    "implementation_planner",
    implementation_planner
)

graph.add_node(
    "risk_change_reviewer",
    risk_change_reviewer
)

graph.add_node(
    "report_generator",
    report_generator
)

# =========================
# MAIN FLOW
# =========================

graph.add_edge(START, "intent_router")

graph.add_conditional_edges(
    "intent_router",
    intent_route,
    {
        "analysis": "business_profiler",
        "chat": "chat_agent",
    })
graph.add_edge("chat_agent",END)
graph.add_edge("business_profiler", "missing_info")
graph.add_conditional_edges("missing_info",missing_info_router,{"need_more_info": "clarification_node","continue": "diagnosis_agent"})
graph.add_edge("clarification_node","merge_clarification")
graph.add_edge("merge_clarification","business_profiler")
graph.add_edge("diagnosis_agent", "problem_classifier")
graph.add_edge("problem_classifier", "planner")
graph.add_edge("planner", "dynamic_agent_selection")

# =========================
# PARALLEL RESEARCH
# =========================

graph.add_conditional_edges(
    "dynamic_agent_selection",
    route_agents
)

graph.add_edge(
    "market_agent",
    "research_synthesizer"
)

graph.add_edge(
    "competitor_agent",
    "research_synthesizer"
)

graph.add_edge(
    "marketing_agent",
    "research_synthesizer"
)

graph.add_edge(
    "operations_agent",
    "research_synthesizer"
)

graph.add_edge(
    "finance_agent",
    "research_synthesizer"
)

graph.add_edge(
    "customer_agent",
    "research_synthesizer"
)

# =========================
# CONSULTING LOOP
# =========================

graph.add_edge(
    "research_synthesizer",
    "consultant_agent"
)

graph.add_edge(
    "consultant_agent",
    "judge_agent"
)

graph.add_edge(
    "judge_agent",
    "research_gap_analyzer"
)

graph.add_conditional_edges(
    "research_gap_analyzer",
    judge_router,
    {
        "replan": "replanning_agent",
        "continue": "recommendation_prioritizer",
    },
)

graph.add_edge(
    "replanning_agent",
    "targeted_research"
)

graph.add_edge(
    "targeted_research",
    "consultant_agent"
)

# =========================
# OUTPUT PIPELINE
# =========================

graph.add_edge(
    "recommendation_prioritizer",
    "implementation_planner"
)

graph.add_edge(
    "implementation_planner",
    "risk_change_reviewer"
)

graph.add_edge(
    "risk_change_reviewer",
    "report_generator"
)

graph.add_edge(
    "report_generator",
    END
)



from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()

workflow = graph.compile(
    checkpointer=checkpointer
)