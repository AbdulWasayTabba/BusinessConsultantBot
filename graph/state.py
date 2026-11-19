from operator import add
from typing import Annotated, Any, Literal, TypedDict


class BizGPTState(TypedDict):
    # User Input
    user_input: str

    # Routing
    route_type: str

    # Business Understanding
    business_profile: dict[str, Any]

    # missing info
    missing_fields: list[str]
    clarification_question: str

    user_clarification: str
    clarification_attempts: int

    # Problem Analysis
    diagnosis: dict[str, Any]
    problem_categories: list[str]
    # Planning
    research_plan: list[str]
    selected_agents: list[
        Literal[
            "market_agent",
            "competitor_agent",
            "marketing_agent",
            "operations_agent",
            "finance_agent",
            "customer_agent",
        ]
    ]

    # Research Phase
    research_findings: Annotated[list[dict[str, Any]], add]

    # Synthesis Phase
    synthesized_insights: list[str]
    research_gaps: dict[str, list[str]]
    replan_count: int

    # Consulting Phase
    recommendations: list[str]

    # Self Reflection / Judge
    judge_feedback: dict[str, Any]

    # Prioritization
    prioritized_actions: list[dict[str, Any]]

    # Execution Planning
    implementation_plan: dict[str, Any]

    # Risk Review
    risk_review: dict[str, Any]

    # Final Output
    final_report: dict[str, Any]
