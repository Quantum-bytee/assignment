import os
import json
import streamlit as st
from pdf_parser import parse_pdf
from extractor import llm_extract, extract_and_summary_prompt, chat_qa_prompt_template
import re

st.set_page_config(page_title="GeM Tender Parser")

st.title("GeM Tender Parser")

uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file is not None:
    # Save uploaded file to a temporary location
    temp_pdf_path = "temp_uploaded.pdf"
    with open(temp_pdf_path, "wb") as f:
        f.write(uploaded_file.read())

    # Parse text from uploaded PDF
    text = parse_pdf(temp_pdf_path)

    # Run extraction prompt
    result_text = llm_extract(text, extract_and_summary_prompt)

    # Extract JSON and summary
    json_match = re.search(r"\[START_JSON\](.*?)\[END_JSON\]", result_text, re.DOTALL)
    summary_match = re.search(r"\[START_SUMMARY\](.*?)\[END_SUMMARY\]", result_text, re.DOTALL)

    extracted_data = None
    summary_text = ""

    if json_match:
        json_text = json_match.group(1).strip()
        try:
            extracted_data = json.loads(json_text)
        except json.JSONDecodeError:
            st.error("LLM returned invalid JSON data.")
    else:
        st.warning("No JSON section found.")

    if summary_match:
        summary_text = summary_match.group(1).strip()
    else:
        st.warning("No summary section found.")

    if summary_text:
        st.subheader("Tender Summary:")
        st.write(summary_text)

    if extracted_data:
        st.subheader("Extracted Data (JSON):")
        st.json(extracted_data)

    st.subheader("Ask a question about this tender:")
    user_question = st.text_input("Your question:")

    if user_question:
        qa_prompt = chat_qa_prompt_template.format(
            user_question=user_question,
            json_data=json.dumps(extracted_data, indent=2) if extracted_data else "None",
            text=text
        )

        answer = llm_extract(text, qa_prompt)
        st.markdown("### Answer:")
        st.write(answer)
