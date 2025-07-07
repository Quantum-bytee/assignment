from pdf_parser import parse_pdf
from extractor import rule_based_extract, llm_extract, extract_and_summary_prompt
import re
import json

def main(pdf_path, use_llm=False):
    print(f"Processing PDF: {pdf_path}\n")

    text = parse_pdf(pdf_path)

    if use_llm:
        result_text = llm_extract(text, extract_and_summary_prompt)

        # Extract JSON
        json_match = re.search(r"\[START_JSON\](.*?)\[END_JSON\]", result_text, re.DOTALL)
        summary_match = re.search(r"\[START_SUMMARY\](.*?)\[END_SUMMARY\]", result_text, re.DOTALL)

        if json_match:
            json_text = json_match.group(1).strip()
            try:
                result_json = json.loads(json_text)
                print("Extracted JSON Data:\n")
                print(json.dumps(result_json, indent=2))
            except json.JSONDecodeError:
                print("invalid JSON data:\n")
                print(json_text)
        else:
            print("No JSON section found.")

        if summary_match:
            summary_text = summary_match.group(1).strip()
            print("\nSummary:")
            print(summary_text)
        else:
            print("No summary section found.")

    else:
        result = rule_based_extract(text)
        print("Rule-Based Extracted Data:\n", result)
