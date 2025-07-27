import json
import re
from app.settings import CRITERIA_PATH
from app.core.llm import query_llm

def load_criteria():
    # Try to load NCQA criteria first, fallback to original criteria
    try:
        ncqa_path = CRITERIA_PATH.replace('audit_criteria.json', 'ncqa_audit_criteria.json')
        with open(ncqa_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
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
            compliance_score_match = re.search(r'"compliance_score":\s*(\d+)', response)
            risk_level_match = re.search(r'"risk_level":\s*"([^"]*)"', response)
            
            if found_match:
                return {
                    "found": found_match.group(1).lower() == "true",
                    "evidence": evidence_match.group(1) if evidence_match else "",
                    "explanation": explanation_match.group(1) if explanation_match else "",
                    "remarks": remarks_match.group(1) if remarks_match else "",
                    "compliance_score": int(compliance_score_match.group(1)) if compliance_score_match else 0,
                    "risk_level": risk_level_match.group(1) if risk_level_match else "Unknown"
                }
        except Exception:
            pass
    
    return None

def create_ncqa_audit_prompt(criteria_item, text):
    """Create a comprehensive NCQA audit prompt for healthcare compliance"""
    
    prompt = f"""
You are a healthcare compliance auditor specializing in NCQA standards. Audit this document against the specific criterion.

CRITERIA: {criteria_item.get('criteria', 'N/A')}
Category: {criteria_item.get('category', 'N/A')}
Factor: {criteria_item.get('factor', 'N/A')}

COMPLIANCE REQUIREMENTS:
{chr(10).join([f"- {req}" for req in criteria_item.get('compliance_requirements', [])])}

DOCUMENT TO AUDIT:
{text}

INSTRUCTIONS:
1. ONLY respond if you find specific evidence supporting this criterion
2. If no evidence is found, DO NOT respond at all (save tokens)
3. If evidence is found, respond with ONLY this JSON:

{{
    "evidence": "[specific text or evidence found]",
    "explanation": "[how this evidence demonstrates compliance]",
    "remarks": "[additional observations or recommendations]",
    "compliance_score": [0-100],
    "risk_level": "Low|Medium|High|Critical"
}}

CRITICAL: If no evidence exists, return nothing. Do not explain why no evidence was found.
"""
    return prompt

def run_audit_on_text(text: str, model: str = None, provider: str = None):
    criteria = load_criteria()
    results = []
    
    for c in criteria:
        # Use NCQA-specific prompt if available, otherwise use generic prompt
        if 'compliance_requirements' in c:
            prompt = create_ncqa_audit_prompt(c, text)
        else:
            # Fallback to original prompt format
            prompt = (
                f"Audit the following document for this criterion: '{c['criteria']}'. "
                f"Category: {c['category']}. "
                f"Description: {c['description']}.\n"
                f"Document:\n{text}\n"
                "Respond in JSON format with keys: 'found' (true/false), 'evidence' (string), 'explanation' (string), 'remarks' (string). "
                "Do not include markdown formatting or code blocks, just the raw JSON object."
            )
        
        try:
            llm_response = query_llm(prompt, model, 0.1, provider)  # Lower temperature for more consistent results
            
            # Use the improved JSON extraction function
            parsed = extract_json_from_response(llm_response)
            
            if parsed and isinstance(parsed, dict):
                found = parsed.get('found', False)
                evidence = parsed.get('evidence', '')
                explanation = parsed.get('explanation', '')
                remarks = parsed.get('remarks', '')
                compliance_score = parsed.get('compliance_score', 0)
                risk_level = parsed.get('risk_level', 'Unknown')
            else:
                found = False
                evidence = ''
                explanation = f"LLM response could not be parsed: {llm_response[:200]}..."
                remarks = ''
                compliance_score = 0
                risk_level = 'Unknown'
        except Exception as e:
            found = False
            evidence = ''
            explanation = f"LLM error: {str(e)}"
            remarks = ''
            compliance_score = 0
            risk_level = 'Unknown'
        
        results.append({
            "criteria": c["criteria"],
            "category": c["category"],
            "factor": c.get("factor", ""),
            "evidence": evidence,
            "explanation": explanation,
            "remarks": remarks,
            "compliance_score": compliance_score,
            "risk_level": risk_level,
            "page": None  # Page extraction not implemented in LLM mode
        })
    return results 

def run_audit_on_text_by_page(pages: list[dict[str, str]], model: str = None, provider: str = None):
    criteria = load_criteria()
    results = []

    for page in pages:
        page_number = page["page"]
        page_text = page["text"]

        for c in criteria:
            if 'compliance_requirements' in c:
                prompt = create_ncqa_audit_prompt(c, page_text)
            else:
                # Token-efficient prompt: LLM only responds if evidence is found
                prompt = (
                    f"Audit this document page against the criterion: '{c['criteria']}'\n"
                    f"Category: {c['category']}\n"
                    f"Description: {c['description']}\n\n"
                    f"Document (Page {page_number}):\n{page_text}\n\n"
                    f"INSTRUCTIONS:\n"
                    f"1. ONLY respond if you find specific evidence supporting this criterion\n"
                    f"2. If no evidence is found, DO NOT respond at all (save tokens)\n"
                    f"3. If evidence is found, respond with ONLY this JSON:\n"
                    f"{{\n"
                    f"  \"evidence\": \"[specific text or description of evidence]\",\n"
                    f"  \"explanation\": \"[how this evidence supports the criterion]\",\n"
                    f"  \"remarks\": \"[additional notes]\",\n"
                    f"  \"compliance_score\": [0-100],\n"
                    f"  \"risk_level\": \"Low|Medium|High\"\n"
                    f"}}\n\n"
                    f"CRITICAL: If no evidence exists, return nothing. Do not explain why no evidence was found."
                )

            try:
                llm_response = query_llm(prompt, model, 0.1, provider)
                parsed = extract_json_from_response(llm_response)
                # print(f"llm_response: {llm_response}")

                # Since LLM only responds when evidence is found, simple validation is sufficient
                if parsed and isinstance(parsed, dict) and parsed.get("evidence"):
                    evidence = parsed.get("evidence", "")
                    if evidence.strip():  # Basic check for non-empty evidence
                        results.append({
                            "criteria": c["criteria"],
                            "category": c["category"],
                            "factor": c.get("factor", ""),
                            "evidence": evidence,
                            "explanation": parsed.get("explanation", ""),
                            "remarks": parsed.get("remarks", ""),
                            "compliance_score": parsed.get("compliance_score", 0),
                            "risk_level": parsed.get("risk_level", "Unknown"),
                            "page": page_number
                        })

            except Exception as e:
                # Log error and continue with next
                print(f"Error processing criteria '{c['criteria']}': {str(e)}")
                continue

    return results


