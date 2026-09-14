from dotenv import load_dotenv
load_dotenv()

from langgraph.types import Command
from graph.graph import workflow


config = {
    "configurable": {
        "thread_id": "test-session-3"
    }
}

print("\n🚀 Starting BizGPT Workflow...\n")

# Initial Run
result = workflow.invoke(
    {
        "user_input": "My sales are down.",
        "replan_count": 0,
        "research_findings": [],
        "clarification_attempts": 0
    },
    config=config
)

print("\n==============================")
print("FIRST RESPONSE")
print("==============================")
print(result)

# Attempt 1
result = workflow.invoke(
    Command(
        resume="I don't know."
    ),
    config=config
)

print("\n==============================")
print("AFTER ATTEMPT 1")
print("==============================")
print(result)

# Attempt 2
result = workflow.invoke(
    Command(
        resume="Not sure."
    ),
    config=config
)

print("\n==============================")
print("AFTER ATTEMPT 2")
print("==============================")
print(result)

# Attempt 3 (Good Answer)
result = workflow.invoke(
    Command(
        resume="""
        Industry: Retail
        Revenue: $1M
        Employees: 25
        Location: Karachi
        """
    ),
    config=config
)

print("\n==============================")
print("FINAL RESULT")
print("==============================")
print(result)