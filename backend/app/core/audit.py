import json
import re
from app.settings import CRITERIA_PATH
from app.core.llm import query_llm

def load_criteria():
    with open(CRITERIA_PATH, 'r') as f:
        return json.load(f)

def extract_json_from_response(response: str):
    """Extract JSON from LLM response, handling markdown code blocks and other formatting"""
    # Remove markdown code blocks
    response = re.sub(r'```json\s*', '', response)
    response = re.sub(r'```\s*$', '', response)
    response = response.strip()
    
    # Try to find JSON object in the response
    try:
        # First, try to parse the entire response as JSON
        return json.loads(response)
    except json.JSONDecodeError:
        # If that fails, try to extract JSON object using regex
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        # If still no luck, try to extract key-value pairs manually
        try:
            # Look for common patterns in the response
            found_match = re.search(r'"found":\s*(true|false)', response, re.IGNORECASE)
            evidence_match = re.search(r'"evidence":\s*"([^"]*)"', response)
            explanation_match = re.search(r'"explanation":\s*"([^"]*)"', response)
            remarks_match = re.search(r'"remarks":\s*"([^"]*)"', response)
            
            if found_match:
                return {
                    "found": found_match.group(1).lower() == "true",
                    "evidence": evidence_match.group(1) if evidence_match else "",
                    "explanation": explanation_match.group(1) if explanation_match else "",
                    "remarks": remarks_match.group(1) if remarks_match else ""
                }
        except Exception:
            pass
    
    return None

def run_audit_on_text(text: str, model: str = None, provider: str = None):
    criteria = load_criteria()
    results = []
    for c in criteria:
        # Build a prompt for the LLM
        prompt = (
            f"Audit the following document for this criterion: '{c['criteria']}'. "
            f"Category: {c['category']}. "
            f"Description: {c['description']}.\n"
            f"Document:\n{text}\n"
            "Respond in JSON format with keys: 'found' (true/false), 'evidence' (string), 'explanation' (string), 'remarks' (string). "
            "Do not include markdown formatting or code blocks, just the raw JSON object."
        )
        try:
            llm_response = query_llm(prompt, model, 0.2, provider)
            
            # Use the improved JSON extraction function
            parsed = extract_json_from_response(llm_response)
            
            if parsed and isinstance(parsed, dict):
                found = parsed.get('found', False)
                evidence = parsed.get('evidence', '')
                explanation = parsed.get('explanation', '')
                remarks = parsed.get('remarks', '')
            else:
                found = False
                evidence = ''
                explanation = f"LLM response could not be parsed: {llm_response[:200]}..."
                remarks = ''
        except Exception as e:
            found = False
            evidence = ''
            explanation = f"LLM error: {str(e)}"
            remarks = ''
        results.append({
            "criteria": c["criteria"],
            "category": c["category"],
            "evidence": evidence,
            "explanation": explanation,
            "remarks": remarks,
            "page": None  # Page extraction not implemented in LLM mode
        })
    return results 