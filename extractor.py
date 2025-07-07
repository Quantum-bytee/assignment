import google.generativeai as genai
import os
import re
from dotenv import load_dotenv
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def rule_based_extract(text):
    """
    Basic regex-based extraction of some example fields from the PDF text.
    You can extend this to more fields as needed.
    """
    data = {}
    bid_date = re.search(r"Bid End Date.*?(\d{2}-\w+-\d{4})", text, re.IGNORECASE)
    if bid_date:
        data["Bid End Date"] = bid_date.group(1)

    quantity = re.search(r"Quantity.*?(\d+)", text, re.IGNORECASE)
    if quantity:
        data["Quantity"] = quantity.group(1)

    item_category = re.search(r"Item Category.*?:\s*(.*)", text, re.IGNORECASE)
    if item_category:
        data["Item Category"] = item_category.group(1).strip()

    buyer_org = re.search(r"Buyer Organization Name.*?:\s*(.*)", text, re.IGNORECASE)
    if buyer_org:
        data["Buyer Organization Name"] = buyer_org.group(1).strip()

    return data

def llm_extract(text, prompt_template):
    """
    Calls Google Gemini API for text extraction or summarization.
    """
    model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

    prompt = f"{prompt_template}\n\n{text}"

    response = model.generate_content(prompt)

    return response.text

extract_and_summary_prompt = """
You are an intelligent information extraction agent.

From the document text below:

1. Extract the following fields and return them as JSON:
    - Bid Number
    - Bid Offer Validity
    - Organization Name
    - Bid Opening Date
    - Bid End Date
    - Item Category
    - Quantity
    - Buyer Organization Name
    - procurement_item

    If a field is not found, set it to null.

2. Then, separately, generate a short English summary of 2-3 sentences describing:
    - What item is being procured
    - The organization and address if available
    - Bid start/end dates
    - Quantity and category of the item

Output your answer in this exact format:

[START_JSON]
{ ... JSON object here ... }
[END_JSON]

[START_SUMMARY]
Summary text here.
[END_SUMMARY]
"""

chat_qa_prompt_template = """
You are an intelligent chatbot for Government e-Marketplace tenders.

Answer the following user question based on the JSON data and the full tender text.

User question:
{user_question}

JSON data:
{json_data}

Tender document text:
{text}

Return only the answer as plain text.
"""
