import asyncio
import json

from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_groq import ChatGroq

from traceforge.core.decorators import trace_step  # Import your new decorator
from traceforge.core.manager import TraceManager
from traceforge.exporters.base import set_exporter
from traceforge.exporters.json_file import JSONExporter
from traceforge.instrumentation.agent_wrapper import wrap_agent

# 1. Setup
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    api_key="",
)
set_exporter(JSONExporter())
tm = TraceManager(project="multi-step-system")

# --- INTERMEDIATE STEPS (TRACED) ---


@trace_step(name="Language Detection", span_type="tool")
async def detect_language(text: str):
    # Simulate detection logic
    return "French" if "bonjour" in text.lower() else "English"


@trace_step(name="Query Rewriter", span_type="tool")
async def rewrite_query(text: str):
    # Simulate cleaning/rewriting query for the agent
    return f"{text} (Please provide a step-by-step calculation)"


@trace_step(name="Vector Retrieval", span_type="tool")
async def get_context(query: str):
    # Simulate RAG retrieval
    return ["Math Reference: Addition is sum of parts."]


# --- AGENT SETUP ---


@tool
def add_numbers_tool(input_text: str) -> str:
    """Adds numbers separated by spaces"""
    return str(sum(map(int, input_text.split())))


agent = create_agent(llm, system_prompt="You are a helper.", tools=[add_numbers_tool])

agent = wrap_agent(agent, method_name="invoke", name="LangChainAgent")


async def main():
    current_session = "user-222"

    # 2. THE FLOW: Everything inside here is part of the same Trace
    with tm.start(library="langchain", metadata={"session_id": current_session}):
        user_input = "Add 10 and 3"

        # Step 1: Detect Language
        lang = await detect_language(user_input)

        # Step 2: Rewrite
        clean_query = await rewrite_query(user_input)

        # Step 3: Retrieve Context
        context = await get_context(clean_query)

        # Step 4: The Agent Call
        # TraceForge connects this to the same 'user-111' session automatically
        query = {
            "messages": [{"role": "user", "content": clean_query}],
            "context": context,
        }
        result = agent.invoke(query)

        print(f"Final Agent Result: {json.dumps(result, indent=2)}")


if __name__ == "__main__":
    asyncio.run(main())
