"""BizGPTState contract: keys the graph routers rely on must exist."""

import pytest

pytest.importorskip("typing_extensions")
from graph.state import BizGPTState  # noqa: E402


@pytest.mark.parametrize(
    "key",
    ["user_input", "route_type", "missing_fields", "clarification_attempts", "selected_agents"],
)
def test_state_has_key(key):
    assert key in BizGPTState.__annotations__
