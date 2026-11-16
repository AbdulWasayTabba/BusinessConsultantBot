"""Graph wiring + router logic. Pure functions only: no LLM is ever invoked."""
import pytest

pytest.importorskip("langgraph")
g = pytest.importorskip("graph.graph")


def test_workflow_compiles_with_expected_nodes():
    nodes = set(g.workflow.get_graph().nodes)
    for name in ["intent_router", "planner", "judge_agent", "report_generator", "market_agent"]:
        assert name in nodes


@pytest.mark.parametrize(
    "route,expected", [("business_analysis", "analysis"), ("chat", "chat"), (None, "chat")]
)
def test_intent_route(route, expected):
    assert g.intent_route({"route_type": route}) == expected


def test_route_agents_fans_out_one_send_per_agent():
    sends = g.route_agents({"selected_agents": ["market_agent", "finance_agent"]})
    assert [s.node for s in sends] == ["market_agent", "finance_agent"]


def test_judge_router_replans_once_then_continues():
    state = {
        "judge_feedback": {"research_needed": True},
        "research_gaps": {"prioritized_gaps": ["pricing"]},
        "replan_count": 0,
    }
    assert g.judge_router(state) == "replan"
    assert g.judge_router({**state, "replan_count": 1}) == "continue"
    assert g.judge_router({}) == "continue"


def test_missing_info_router_caps_attempts():
    assert g.missing_info_router({"missing_fields": ["industry"], "clarification_attempts": 0}) == "need_more_info"
    assert g.missing_info_router({"missing_fields": ["industry"], "clarification_attempts": 3}) == "continue"
    assert g.missing_info_router({"missing_fields": []}) == "continue"
