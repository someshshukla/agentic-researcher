
from agent import run_agent

if __name__ == "__main__":
    try:
        query = input("What can I help you research? ")
        structured, raw_text, raw = run_agent(query)
        print(raw_text)
    except KeyboardInterrupt:
        pass
