from typing import TypedDict, List, Dict, Any,Annotated,Literal
from operator import add

class BizGPTState(TypedDict):
    # User Input
    user_input: str

    # Routing
    route_type: str

    # Business Understanding
    business_profile: Dict[str, Any]

    #missing info
    missing_fields: list[str]
    clarification_question: str

    user_clarification: str
    clarification_attempts: int

    # Problem Analysis
    diagnosis: Dict[str, Any]
    problem_categories: List[str]
    # Planning
    research_plan: List[str]
    selected_agents: list[Literal[
"market_agent",
"competitor_agent",
"marketing_agent",
"operations_agent",
"finance_agent",
"customer_agent"
]]

    # Research Phase
    research_findings: Annotated[list[dict[str, Any]],add]

    # Synthesis Phase
    synthesized_insights: List[str]
    research_gaps: Dict[str, List[str]]
    replan_count: int

    # Consulting Phase
    recommendations: List[str]

    # Self Reflection / Judge
    judge_feedback: Dict[str, Any]

    # Prioritization
    prioritized_actions: List[Dict[str, Any]]

    # Execution Planning
    implementation_plan: Dict[str, Any]

    # Risk Review
    risk_review: Dict[str, Any]

    # Final Output
    final_report: Dict[str, Any]