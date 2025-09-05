
import streamlit as st
from agent import run_agent, ResearchResponse
import json
from tools import save_to_txt

st.set_page_config(page_title="Inquestor (Gemini 1.5 Flash)", layout="centered")

st.title(" Inquestor ")
st.write("Ask for any topic. The agent can search, consult Wikipedia, and save results.")

with st.sidebar:
    st.header("Settings")
    st.caption("")
    save_to_file = st.checkbox("Save output to research_output.txt", value=True)

query = st.text_area("What can I help you research?", height=120, placeholder="e.g., The impact of quantum dots in modern displays")

if st.button("Run Research", type="primary") and query.strip():
    with st.spinner("Running agent..."):
        structured, raw_text, raw = run_agent(query.strip())

    if structured:
        st.subheader("Structured Result")
        st.markdown(f"**Topic:** {structured.topic}")
        st.markdown("**Summary:**")
        st.write(structured.summary)
        if structured.sources:
            st.markdown("**Sources:**")
            for s in structured.sources:
                st.write("-", s)
        if structured.tools_used:
            st.markdown("**Tools used:** " + ", ".join(structured.tools_used))

        if save_to_file:
            msg = save_to_txt(raw_text)
            st.success(msg)
    else:
        st.warning("Could not parse structured output. Showing raw text below.")
        st.code(raw_text)

    # Always offer a JSON download 
    payload = {}
    if structured:
        payload = {
            "topic": structured.topic,
            "summary": structured.summary,
            "sources": structured.sources,
            "tools_used": structured.tools_used,
        }
    else:
        payload = {"raw_text": raw_text}

    st.download_button(
        "Download JSON",
        data=json.dumps(payload, ensure_ascii=False, indent=2),
        file_name="research_result.json",
        mime="application/json",
    )
