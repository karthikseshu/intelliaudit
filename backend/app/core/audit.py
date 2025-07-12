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
You are a healthcare compliance auditor specializing in NCQA (National Committee for Quality Assurance) standards. Your task is to audit a healthcare document against specific NCQA criteria.

CRITERIA DETAILS:
- ID: {criteria_item.get('id', 'N/A')}
- Category: {criteria_item.get('category', 'N/A')}
- Factor: {criteria_item.get('factor', 'N/A')}
- Criteria: {criteria_item.get('criteria', 'N/A')}
- Description: {criteria_item.get('description', 'N/A')}

COMPLIANCE REQUIREMENTS:
{chr(10).join([f"- {req}" for req in criteria_item.get('compliance_requirements', [])])}

EVIDENCE REQUIRED:
{chr(10).join([f"- {evidence}" for evidence in criteria_item.get('evidence_required', [])])}

DOCUMENT TO AUDIT:
{text}

INSTRUCTIONS:
1. Carefully analyze the document for evidence of compliance with this NCQA criterion
2. Look for specific mentions, policies, procedures, or documentation that address the requirements
3. Consider both explicit statements and implicit evidence that demonstrates compliance
4. Evaluate the completeness and adequacy of the evidence found

RESPOND IN THIS EXACT JSON FORMAT (no markdown, no code blocks):
{{
    "found": true/false,
    "evidence": "Specific text or evidence found in the document that supports compliance",
    "explanation": "Detailed explanation of how the evidence demonstrates compliance or why it's insufficient",
    "remarks": "Additional observations, recommendations, or areas of concern",
    "compliance_score": 0-100,
    "risk_level": "Low/Medium/High/Critical"
}}

COMPLIANCE SCORING GUIDE:
- 90-100: Fully compliant with strong evidence
- 70-89: Mostly compliant with minor gaps
- 50-69: Partially compliant with significant gaps
- 30-49: Minimally compliant with major concerns
- 0-29: Non-compliant or insufficient evidence

RISK LEVEL ASSESSMENT:
- Low: Minor compliance gaps with low impact
- Medium: Moderate gaps that may affect quality
- High: Significant gaps that could impact patient care
- Critical: Major compliance failures requiring immediate attention

Be thorough, objective, and provide specific evidence from the document. If no evidence is found, clearly state this and explain what should be present for compliance.
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