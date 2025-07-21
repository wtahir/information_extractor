import os
from openai import AzureOpenAI
from dotenv import load_dotenv
from schemas import ExtractionResult
import re
import json


load_dotenv()
client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version=os.getenv("AZURE_API_VERSION")
)


FIELD_MAPPING = {
    "Payee": "payee",
    "Total_amount": "amount",
    "Is_amount_gross_or_net": "amount_type",
    "IBAN": "iban"
}

# 🧼 GPT cleanup: Remove markdown ``` and find valid JSON block
def extract_json_object(text):
    cleaned = re.sub(r"```(?:json)?", "", text).strip("`").strip()
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in response.")
    return match.group(0)

# 🧠 Normalize field names to match schema
def normalize_keys(json_data: dict):
    def is_missing(value):
        return isinstance(value, str) and "not provided" in value.lower()

    normalized = {}
    for key, value in json_data.items():
        new_key = FIELD_MAPPING.get(key.strip(), key.strip()).lower()
        if is_missing(value):
            normalized[new_key] = None
        else:
            normalized[new_key] = value
    return normalized

# 🔄 Coerce strings to correct types (e.g., float)
def coerce_types(data):
    if "amount" in data and isinstance(data["amount"], str):
        try:
            data["amount"] = float(data["amount"])
        except:
            data["amount"] = None
    return data

# 📤 Extract fields using Azure GPT-4o
def extract_fields(text: str) -> str:
    prompt = f"""
    Extract the following fields from the insurance document text.

    Use these exact JSON keys:
    - payee: the recipient of the payment
    - amount: the numeric value of the total amount (do not include currency)
    - amount_type: one of "gross", "net", or "unknown"
    - iban: the bank account number if available

    If a field is missing, write null.

    Only return raw JSON using these keys. No currency. No explanation.
    Document text:
    {text}
    """


    response = client.chat.completions.create(
        model=os.getenv("AZURE_DEPLOYMENT_NAME"),
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return response.choices[0].message.content.strip()

# ✅ Validate and parse GPT response
def parse_response(response_str: str):
    try:
        json_text = extract_json_object(response_str)
        raw_dict = json.loads(json_text)
        normalized = normalize_keys(raw_dict)
        coerced = coerce_types(normalized)
        parsed = ExtractionResult.model_validate(coerced)
        return parsed.dict(), None
    except Exception as e:
        return None, str(e)