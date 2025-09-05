from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
# agent.py
from tools import tools  # instead of individual names
...

# Load environment variables (GOOGLE_API_KEY)
load_dotenv()


# ---------- Data Models ----------

class ResearchResponse(BaseModel):
    """Structured shape for the agent's final answer."""
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str]


# ---------- LLM + Prompt Setup ----------

# Gemini 1.5 Flash via LangChain wrapper
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.3,
)

# Parse model output directly into the Pydantic model
parser = PydanticOutputParser(pydantic_object=ResearchResponse)

# Chat prompt with tool-calling support
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "You are a research assistant that will help generate a research paper.\n"
                "Answer the user query and use necessary tools when helpful.\n"
                "Wrap the output in this format and provide no other text\n"
                "{format_instructions}"
            ),
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
).partial(format_instructions=parser.get_format_instructions())

# Available tools


agent = create_tool_calling_agent(llm=llm, prompt=prompt, tools=tools)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


# ---------- Public API ----------

def run_agent(query: str):
    """
    Run the agent on a user query.

    Returns:
        tuple[ResearchResponse | None, str, dict]:
            - structured: Parsed ResearchResponse if parsing succeeds, else None.
            - raw_text: The raw string returned by the agent.
            - raw: The raw dict returned by the AgentExecutor.
    """
    raw = agent_executor.invoke({"query": query})

    # AgentExecutor returns a dict; final text is commonly under "output"
    raw_text = raw.get("output", "") if isinstance(raw, dict) else str(raw)

    structured = None
    try:
        structured = parser.parse(raw_text)
    except Exception:
# If the model added extra text around the JSON, try to extract just the JSON part
        import json
        import re

        match = re.search(r"\{[\s\S]*\}", raw_text)
        if match:
            try:
                data = json.loads(match.group(0))
                structured = ResearchResponse(**data)
            except Exception:
                structured = None

    return structured, raw_text, raw
