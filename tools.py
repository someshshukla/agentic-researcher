from datetime import datetime
from langchain.tools import Tool
from langchain_community.utilities import WikipediaAPIWrapper

def save_to_txt(data: str, filename: str = "research_output.txt"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"--- Research Output ---\nTimestamp: {timestamp}\n\n{data}\n\n")
    return f"Data successfully saved to {filename}"

save_tool = Tool(
    name="save_text_to_file",
    func=save_to_txt,
    description="Saves structured research data to a text file.",
)

# Wikipedia tool 
api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=1000)
from langchain_community.tools import WikipediaQueryRun
wiki_tool = WikipediaQueryRun(api_wrapper=api_wrapper)


search_tool = None
err_msg = None

try:
    #wrapper
    from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
    ddg = DuckDuckGoSearchAPIWrapper()
    search_tool = Tool(
        name="search",
        description="Search the web for information",
        func=lambda q: "\n".join([r["snippet"] for r in ddg.results(q, max_results=5)]),
    )
except Exception as e_api:
    try:
        # Legacy tool
        from langchain_community.tools import DuckDuckGoSearchRun
        search = DuckDuckGoSearchRun()
        search_tool = Tool(
            name="search",
            func=search.run,
            description="Search the web for information",
        )
    except Exception as e_legacy:
        err_msg = f"(search disabled: {e_api or e_legacy})"


tools = [t for t in [wiki_tool, save_tool, search_tool] if t is not None]


if err_msg:
    print(err_msg)
